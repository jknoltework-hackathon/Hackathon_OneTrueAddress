# Deployment Guide - Render

This guide covers deploying OneTrueAddress to Render.com.

## Quick Answer: Do API Endpoints Need to Change?

**No!** The API endpoints themselves (`/api/v1/match`, `/api/v1/health`, etc.) don't need to change. They are relative paths that work anywhere.

**What changes:** Only the **base URL** changes from `http://localhost:5000` to your Render URL like `https://your-app-name.onrender.com`

## Deployment Steps

### 1. Prerequisites

- GitHub account with your code pushed
- Render account (free tier available at https://render.com)
- `.env` file configured locally (don't commit this!)

### 2. Prepare for Deployment

#### Create `render.yaml` (optional but recommended)
```yaml
services:
  - type: web
    name: onetrueaddress
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn -w 4 -b 0.0.0.0:$PORT web_app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
```

#### Add `gunicorn` to requirements.txt
```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

#### Update web_app.py to use PORT from environment
The current code uses `port=5000` which is fine locally, but Render provides a `PORT` environment variable:

```python
if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
```

### 3. Deploy to Render

#### Option A: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create New Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** `onetrueaddress` (or your preferred name)
     - **Environment:** `Python 3`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn -w 4 -b 0.0.0.0:$PORT web_app:app`
     - **Instance Type:** Free (or paid for production)

3. **Add Environment Variables**
   In Render dashboard, go to "Environment" tab and add:
   ```
   CLAUDE_API_KEY=your_claude_api_key
   GOLDEN_SOURCE_DB_TYPE=postgresql
   GOLDEN_SOURCE_HOST=your_db_host
   GOLDEN_SOURCE_PORT=5432
   GOLDEN_SOURCE_DATABASE=your_db_name
   GOLDEN_SOURCE_USER=your_db_user
   GOLDEN_SOURCE_PASSWORD=your_db_password
   GOLDEN_SOURCE_MATCH_TABLE=team_cool_and_gang.pinellas_fl
   INTERNAL_MATCH_TABLE=team_cool_and_gang.pinellas_fl_baddatascenarios
   FUZZY_MATCH_THRESHOLD=90.0
   CONFIDENCE_THRESHOLD=90.0
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - Wait for deployment to complete (usually 2-5 minutes)

#### Option B: Manual Docker Deployment

If you prefer Docker:

1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD gunicorn -w 4 -b 0.0.0.0:$PORT web_app:app
   ```

2. Follow Render's Docker deployment instructions

### 4. Access Your Deployed API

Once deployed, your app will be available at:
```
https://your-app-name.onrender.com
```

**API Endpoints:**
- Web UI: `https://your-app-name.onrender.com/`
- Health Check: `https://your-app-name.onrender.com/api/v1/health`
- Match Address: `https://your-app-name.onrender.com/api/v1/match`
- All other endpoints follow the same pattern

### 5. Test Your Deployment

#### Using Environment Variable:
```bash
# Set your Render URL
export API_BASE_URL="https://your-app-name.onrender.com/api/v1"

# Test the API
python test_api.py
```

#### Or inline:
```bash
API_BASE_URL="https://your-app-name.onrender.com/api/v1" python test_api.py
```

#### Using curl:
```bash
# Health check
curl https://your-app-name.onrender.com/api/v1/health

# Match address
curl -X POST https://your-app-name.onrender.com/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St, City, FL 12345", "threshold": 90}'
```

#### Python client:
```python
import requests

BASE_URL = "https://your-app-name.onrender.com/api/v1"

response = requests.post(
    f"{BASE_URL}/match",
    json={"address": "123 Main St, City, FL 12345"}
)
print(response.json())
```

### 6. Database Setup on Render

If you need to host your PostgreSQL database on Render:

1. **Create PostgreSQL Database**
   - Click "New +" → "PostgreSQL"
   - Choose free or paid tier
   - Note the connection details

2. **Update Environment Variables**
   - Use the provided connection string or individual values
   - Internal hostname: `your-db-name.internal` (faster, free within Render)
   - External hostname: Available in database details

### 7. Monitoring and Logs

**View Logs:**
- Go to your service in Render dashboard
- Click "Logs" tab
- Monitor real-time logs

**Monitor Performance:**
- Check "Metrics" tab for CPU/Memory usage
- Set up alerts if needed

### 8. Custom Domain (Optional)

To use a custom domain like `api.yourcompany.com`:

1. Go to your service → "Settings" → "Custom Domain"
2. Add your domain
3. Update your DNS records as instructed
4. Wait for DNS propagation (5-30 minutes)

### 9. CI/CD

Render automatically redeploys when you push to your main branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Render automatically deploys the update
```

## Troubleshooting

### Database Connection Issues
- Verify environment variables are set correctly
- Check that database accepts connections from Render IPs
- Use internal hostname for Render-hosted databases

### API Not Responding
- Check logs in Render dashboard
- Verify `PORT` environment variable is being used
- Ensure gunicorn is installed in requirements.txt

### Slow Initial Load
- Free tier apps sleep after 15 minutes of inactivity
- Consider paid tier for always-on service
- Use a keep-alive service if needed

### Environment Variables Not Loading
- Verify `.env` is in `.gitignore` (don't commit it!)
- Set all variables in Render dashboard
- Restart service after adding variables

## Security Considerations

1. **Never commit sensitive data:**
   ```bash
   # Verify .gitignore includes:
   .env
   *.pyc
   __pycache__/
   ```

2. **Use environment variables for:**
   - Database credentials
   - API keys
   - Secret keys

3. **Consider adding authentication:**
   - API keys
   - OAuth
   - JWT tokens

4. **Enable HTTPS only** (Render does this by default)

5. **Rate limiting** (implement in production)

## Cost Optimization

**Free Tier Limitations:**
- App sleeps after 15 minutes of inactivity
- Limited to 512MB RAM
- 0.1 CPU

**When to Upgrade:**
- High traffic volume
- Need always-on service
- Require more resources
- Multiple concurrent users

## Summary

✅ **No code changes needed** - API routes work as-is  
✅ **Just update base URL** - From localhost to your Render URL  
✅ **Use environment variables** - Set in Render dashboard  
✅ **Test with provided script** - `python test_api.py`  

Your API will be accessible at:
```
https://your-app-name.onrender.com/api/v1/[endpoint]
```

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- Project Issues: Open an issue in your GitHub repo

