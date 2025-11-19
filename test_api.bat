@echo off
REM Test script for OneTrueAddress API using curl
REM Works on Windows 10/11 with built-in curl

echo ============================================================
echo Testing OneTrueAddress API
echo ============================================================
echo.

REM Set the API base URL (change this to test local or live)
set API_URL=https://hack-onetrueaddress-r3xv.onrender.com/api/v1
REM For local testing, uncomment the line below:
REM set API_URL=http://localhost:5000/api/v1

echo API Base URL: %API_URL%
echo.

REM Test 1: Health Check
echo [Test 1] Health Check Endpoint
echo GET %API_URL%/health
echo.
curl -s -w "HTTP Status: %%{http_code}\n" "%API_URL%/health"
echo.
echo ------------------------------------------------------------
echo.

REM Test 2: Match Address
echo [Test 2] Match Address Endpoint
echo POST %API_URL%/match
echo.
curl -s -w "\nHTTP Status: %%{http_code}\n" ^
  -H "Content-Type: application/json" ^
  -X POST ^
  -d "{\"address\": \"27466 US HIGHWAY 19 N LOT 64 ST, CLEARWATER, FL 33761\", \"threshold\": 90}" ^
  "%API_URL%/match"
echo.
echo ------------------------------------------------------------
echo.

REM Test 3: Time Saved
echo [Test 3] Time Saved Endpoint
echo GET %API_URL%/time_saved
echo.
curl -s -w "HTTP Status: %%{http_code}\n" "%API_URL%/time_saved"
echo.
echo ------------------------------------------------------------
echo.

echo ============================================================
echo API Test Complete
echo ============================================================
pause

