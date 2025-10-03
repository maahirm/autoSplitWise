#!/usr/bin/env python3
"""
Direct API Key Test - Bypasses dotenv caching
"""

import requests
from dotenv import load_dotenv
import os

def test_api_key_direct():
    """Test API key by reading directly from .env file"""
    print("🔑 Direct Splitwise API Key Test")
    print("=" * 40)
    
    # Read API key directly from file
    try:
        load_dotenv()  # load from .env file
        api_key = os.getenv("SPLITWISE_API_KEY")        
        print(f"🔍 Loaded API key: {api_key}")
        
        if not api_key:
            print("❌ No API key found in environment")
            return False
            
        if api_key in ['your_api_key_here', 'your_actual_api_key_goes_here']:
            print("❌ API key is still a placeholder")
            print("The .env file may not be loading properly")
            return False
            
        print(f"🔍 Testing API key: {api_key[:10]}...{api_key[-4:]}")
        print(f"   Length: {len(api_key)} characters")

        response = requests.get(
            "https://secure.splitwise.com/api/v3.0/get_current_user",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            print(f"✅ SUCCESS!")
            print(f"👤 User: {user.get('first_name', '')} {user.get('last_name', '')}")
            print(f"📧 Email: {user.get('email', 'N/A')}")
            print(f"💰 Default Currency: {user.get('default_currency', 'N/A')}")
            
            print(f"\n🎉 Your API key is working perfectly!")
            print(f"You can now run the full test suite:")
            print(f"   python testAPIs.py")
            return True
            
        elif response.status_code == 401:
            error_data = response.json() if response.content else {}
            print(f"❌ Authentication failed!")
            print(f"   Error: {error_data.get('error', 'Invalid credentials')}")
            print(f"\nThis could mean:")
            print(f"• The API key is invalid or expired")
            print(f"• The API key format is incorrect")
            print(f"• Your Splitwise account doesn't have API access")
            return False
            
        else:
            print(f"⚠️ Unexpected response code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Response: {error_data}")
            except:
                print(f"   Raw response: {response.text[:200]}")
            return False
            
    except FileNotFoundError:
        print("❌ .env file not found!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_api_key_direct()
