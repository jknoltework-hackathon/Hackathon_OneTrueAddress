"""Test script for OneTrueAddress API."""
import requests
import json
import sys
import os


def test_api(base_url=None):
    """Test all API endpoints."""
    # Get base URL from environment variable or default to localhost
    if base_url is None:
        base_url = os.getenv('API_BASE_URL', 'http://localhost:5000/api/v1')
    
    print("=" * 60)
    print("OneTrueAddress API Test Suite")
    print("=" * 60)
    print(f"Base URL: {base_url}\n")
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        data = response.json()
        if data.get('status') == 'ok':
            print(f"   ✓ Health check passed: {data}")
        else:
            print(f"   ✗ Health check failed: {data}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        print(f"   Make sure the server is running: python web_app.py")
        return False
    
    print()
    
    # Test 2: Address Matching
    print("2. Testing Address Matching...")
    test_address = "123 Main St, Anytown, FL 12345"
    try:
        response = requests.post(
            f"{base_url}/match",
            json={
                "address": test_address,
                "threshold": 90
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        data = response.json()
        
        if data.get('success'):
            print(f"   ✓ Match request successful")
            print(f"     Input: {data.get('input_address')}")
            print(f"     Match Found: {data.get('match_found')}")
            print(f"     Confidence: {data.get('confidence')}%")
            print(f"     Golden Source Matches: {data.get('total_golden_source', 0)}")
            print(f"     Internal Matches: {data.get('total_internal', 0)}")
            
            if data.get('match_found'):
                matched = data.get('matched_address', {})
                print(f"     Master Address: {matched.get('MasterAddress', 'N/A')}")
        else:
            print(f"   ✗ Match request failed: {data.get('error')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    
    # Test 3: Invalid Request (should fail)
    print("3. Testing Error Handling...")
    try:
        response = requests.post(
            f"{base_url}/match",
            json={"threshold": 90},  # Missing address
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        data = response.json()
        
        if not data.get('success') and 'error' in data:
            print(f"   ✓ Error handling works correctly")
            print(f"     Error message: {data.get('error')}")
        else:
            print(f"   ✗ Error handling failed")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    
    # Test 4: Time Saved
    print("4. Testing Time Saved Endpoint...")
    try:
        response = requests.get(f"{base_url}/time_saved", timeout=10)
        data = response.json()
        
        if data.get('success'):
            print(f"   ✓ Time saved request successful")
            print(f"     Hours Saved: {data.get('hours_saved', 0)}")
        else:
            print(f"   ✗ Time saved request failed: {data.get('error')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    print("=" * 60)
    print("API Test Complete!")
    print("=" * 60)
    return True


def test_with_custom_address(address, threshold=90, base_url=None):
    """Test API with a custom address."""
    # Get base URL from environment variable or default to localhost
    if base_url is None:
        base_url = os.getenv('API_BASE_URL', 'http://localhost:5000/api/v1')
    
    print("=" * 60)
    print(f"Testing Address: {address}")
    print(f"Threshold: {threshold}%")
    print(f"API Base URL: {base_url}")
    print("=" * 60)
    print()
    
    try:
        response = requests.post(
            f"{base_url}/match",
            json={
                "address": address,
                "threshold": threshold
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        data = response.json()
        
        # Pretty print the response
        print("Response:")
        print(json.dumps(data, indent=2))
        
        print()
        
        if data.get('success') and data.get('match_found'):
            print("Match Summary:")
            print(f"  Confidence: {data.get('confidence')}%")
            print(f"  Golden Source Matches: {data.get('total_golden_source', 0)}")
            print(f"  Internal Matches: {data.get('total_internal', 0)}")
            print(f"  Candidates Searched: {data.get('candidates_searched', 0)}")
            
            if data.get('business_rule_exception'):
                print(f"  ⚠️  BUSINESS RULE EXCEPTION: Below threshold")
            
            matched = data.get('matched_address', {})
            if matched:
                print(f"\nBest Match:")
                print(f"  Master Address: {matched.get('MasterAddress', 'N/A')}")
                print(f"  Source: {matched.get('_source_type', 'N/A')}")
                print(f"  Similarity: {matched.get('_similarity_score', 0)}%")
        elif data.get('success'):
            print("No match found")
        else:
            print(f"Error: {data.get('error')}")
        
        return data
        
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Usage:")
            print("  python test_api.py                    # Run full test suite")
            print('  python test_api.py "123 Main St..."   # Test specific address')
            print('  python test_api.py "address" 85       # Test with custom threshold')
            print()
            print("Environment Variables:")
            print("  API_BASE_URL - Base URL for API (default: http://localhost:5000/api/v1)")
            print()
            print("Examples:")
            print("  # Local testing")
            print("  python test_api.py")
            print()
            print("  # Test against Render deployment")
            print('  export API_BASE_URL="https://your-app.onrender.com/api/v1"')
            print("  python test_api.py")
            print()
            print("  # One-line with custom URL")
            print('  API_BASE_URL="https://your-app.onrender.com/api/v1" python test_api.py')
            sys.exit(0)
        
        # Test with custom address
        address = sys.argv[1]
        threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 90
        test_with_custom_address(address, threshold)
    else:
        # Run full test suite
        test_api()

