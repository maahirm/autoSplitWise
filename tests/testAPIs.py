#!/usr/bin/env python3
"""
Splitwise API Testing Script

This script provides comprehensive testing for the Splitwise API.
It includes authentication setup, testing of all major endpoints,
and detailed response analysis.

Usage:
1. Get your API key from Splitwise (Settings -> Account -> API Keys)
2. Create a .env file with: SPLITWISE_API_KEY=your_api_key_here
3. Run: python testAPIs.py

API Documentation: https://dev.splitwise.com/
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from tabulate import tabulate
from dotenv import load_dotenv

class SplitwiseAPITester:
    """
    A comprehensive tester for the Splitwise API
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the API tester"""
        self.base_url = "https://secure.splitwise.com/api/v3.0"
        self.api_key = api_key or os.getenv('SPLITWISE_API_KEY')
        
        if not self.api_key:
            raise ValueError("API key is required. Set SPLITWISE_API_KEY environment variable or pass it directly.")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """
        Make a request to the Splitwise API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            Dictionary containing response data and metadata
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )
            
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'headers': dict(response.headers),
                'url': url
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"JSON decode error: {str(e)}",
                'status_code': response.status_code,
                'raw_content': response.text,
                'url': url
            }
    
    def print_response(self, title: str, response: Dict, verbose: bool = False):
        """Pretty print API response with concise output"""
        print(f"\n🧪 {title}")
        
        if response['success']:
            status_code = response['status_code']
            if status_code == 200:
                print(f"   ✅ SUCCESS (200)")
            elif status_code == 401:
                print(f"   🔐 AUTH FAILED (401)")
            else:
                print(f"   ⚠️ STATUS {status_code}")
            
            # Only show detailed response if verbose or if there's an error
            if verbose or status_code != 200:
                if 'data' in response and response['data']:
                    print(f"   📄 Response: {json.dumps(response['data'], indent=2)[:200]}...")
        else:
            print(f"   ❌ ERROR: {response['error']}")
            if 'status_code' in response:
                print(f"   Status: {response['status_code']}")
    
    def print_summary_response(self, title: str, response: Dict, key_fields: List[str] = None):
        """Print a concise summary of the response"""
        print(f"\n🔍 {title}")
        
        if response['success'] and response.get('status_code') == 200:
            print(f"   ✅ SUCCESS")
            
            data = response.get('data', {})
            if key_fields and data:
                for field in key_fields:
                    if field in data:
                        value = data[field]
                        if isinstance(value, list):
                            print(f"   📊 {field}: {len(value)} items")
                        elif isinstance(value, dict):
                            print(f"   📊 {field}: {len(value)} fields")
                        else:
                            print(f"   📊 {field}: {value}")
        elif response.get('status_code') == 401:
            print(f"   🔐 AUTHENTICATION REQUIRED")
        else:
            print(f"   ❌ FAILED ({response.get('status_code', 'Unknown')})")
            if 'error' in response:
                print(f"   Error: {response['error']}")
    
    # USER ENDPOINTS
    def test_get_current_user(self):
        """Test getting current user information"""
        response = self.make_request('GET', '/get_current_user')
        self.print_summary_response("Current User", response, ['user'])
        return response
    
    # GROUP ENDPOINTS
    def test_get_groups(self):
        """Test getting all groups"""
        response = self.make_request('GET', '/get_groups')
        self.print_summary_response("Groups", response, ['groups'])
        return response
    
    # FRIEND ENDPOINTS
    def test_get_friends(self):
        """Test getting all friends"""
        response = self.make_request('GET', '/get_friends')
        self.print_summary_response("Friends", response, ['friends'])
        return response
    
    # EXPENSE ENDPOINTS
    def test_get_expenses(self, limit: int = 10, group_id: int = None, friend_id: int = None):
        """Test getting expenses"""
        params = {'limit': limit}
        if group_id:
            params['group_id'] = group_id
        if friend_id:
            params['friend_id'] = friend_id
            
        response = self.make_request('GET', '/get_expenses', params=params)
        self.print_summary_response("Expenses", response, ['expenses'])
        return response
    
    # NOTIFICATION ENDPOINTS
    def test_get_notifications(self, limit: int = 10):
        """Test getting notifications"""
        params = {'limit': limit}
        response = self.make_request('GET', '/get_notifications', params=params)
        self.print_summary_response("Notifications", response, ['notifications'])
        return response
    
    # UTILITY ENDPOINTS
    def test_get_currencies(self):
        """Test getting supported currencies"""
        response = self.make_request('GET', '/get_currencies')
        self.print_summary_response("Currencies", response, ['currencies'])
        return response
    
    def test_get_categories(self):
        """Test getting expense categories"""
        response = self.make_request('GET', '/get_categories')
        self.print_summary_response("Categories", response, ['categories'])
        return response
    
    def test_api_key_format(self):
        """Test if the API key format looks correct"""
        print(f"\n🔍 API Key Check: {len(self.api_key)} chars, {self.api_key[:8]}...{self.api_key[-4:]}")
        
        issues = []
        if len(self.api_key) < 20:
            issues.append("too short")
        if ' ' in self.api_key:
            issues.append("contains spaces")
        if self.api_key in ['your_api_key_here', 'your_actual_api_key_goes_here']:
            issues.append("is placeholder")
            
        if issues:
            print(f"   ⚠️ Issues: {', '.join(issues)}")
        else:
            print(f"   ✅ Format looks good")
            
    def test_connection_and_auth(self):
        """Test basic connection and authentication"""
        print(f"\n🔧 Testing Connection & Authentication")
        
        # Quick auth test
        try:
            response = self.session.get(f"{self.base_url}/get_current_user", timeout=10)
            if response.status_code == 200:
                print("   ✅ Authentication successful!")
                return True
            elif response.status_code == 401:
                print("   🔐 Authentication failed - check API key")
                return False
            else:
                print(f"   ⚠️ Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            return False
    
    def run_basic_tests(self):
        """Run a comprehensive set of basic API tests"""
        print("\n🚀 Running Splitwise API Tests")
        
        test_results = []
        
        # Test core endpoints
        tests = [
            ("Current User", self.test_get_current_user),
            ("Currencies", self.test_get_currencies),
            ("Categories", self.test_get_categories),
            ("Groups", self.test_get_groups),
            ("Friends", self.test_get_friends),
            ("Expenses", lambda: self.test_get_expenses(limit=5)),
            ("Notifications", lambda: self.test_get_notifications(limit=5))
        ]
        
        for test_name, test_func in tests:
            try:
                response = test_func()
                if response['success'] and response.get('status_code') == 200:
                    test_results.append([test_name, "✅ Success"])
                elif response.get('status_code') == 401:
                    test_results.append([test_name, "🔐 Auth Error"])
                else:
                    test_results.append([test_name, "❌ Failed"])
            except Exception as e:
                test_results.append([test_name, f"❌ Error"])
        
        # Print summary
        print(f"\n📊 Test Results:")
        print(tabulate(test_results, headers=["Endpoint", "Status"], tablefmt="simple"))
        
        return test_results
    
    def analyze_account_data(self):
        """Analyze and display account data in a user-friendly way"""
        print(f"\n📊 Account Overview")
        
        # Get user info
        user_response = self.make_request('GET', '/get_current_user')
        if user_response['success'] and user_response.get('status_code') == 200:
            user = user_response['data'].get('user', {})
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            print(f"   • {name} ({user.get('email', 'N/A')})")
            print(f"   💰 Currency: {user.get('default_currency', 'N/A')}")
            print(f"   🔔 Notifications: {user.get('notifications_count', 0)}")
        
        # Get groups count
        groups_response = self.make_request('GET', '/get_groups')
        if groups_response['success'] and groups_response.get('status_code') == 200:
            groups = groups_response['data'].get('groups', [])
            print(f"   👥 Groups: {len(groups)}")
            if groups:
                for group in groups[:3]:  # Show first 3 groups
                    print(f"      • {group.get('name', 'Unnamed')}")
        
        # Get friends count
        friends_response = self.make_request('GET', '/get_friends')
        if friends_response['success'] and friends_response.get('status_code') == 200:
            friends = friends_response['data'].get('friends', [])
            print(f"   👫 Friends: {len(friends)}")
        
        # Get recent expenses
        expenses_response = self.make_request('GET', '/get_expenses', params={'limit': 3})
        if expenses_response['success'] and expenses_response.get('status_code') == 200:
            expenses = expenses_response['data'].get('expenses', [])
            print(f"   💸 Recent Expenses: {len(expenses)}")
            for expense in expenses:
                cost = expense.get('cost', '0')
                desc = expense.get('description', 'No description')
                print(f"      • ${cost} - {desc}")


def setup_environment():
    """Setup environment and API key"""
    print("🔧 Loading environment...")
    
    # Force reload environment variables to avoid caching
    if "SPLITWISE_API_KEY" in os.environ:
        del os.environ["SPLITWISE_API_KEY"]
    
    load_dotenv(override=True)
    api_key = os.getenv('SPLITWISE_API_KEY')
    
    if not api_key or api_key in ['your_api_key_here', 'your_actual_api_key_goes_here']:
        print("❌ No valid API key found!")
        print("Please update your .env file with your Splitwise API key")
        return None
    
    print("✅ API key loaded")
    return api_key


def main():
    """Main function to run API tests"""
    print("🏦 Splitwise API Tester")
    
    # Setup environment
    api_key = setup_environment()
    if not api_key:
        return
    
    try:
        # Initialize tester
        tester = SplitwiseAPITester(api_key)
        
        # Quick diagnostics
        tester.test_api_key_format()
        
        # Test authentication
        auth_ok = tester.test_connection_and_auth()
        
        if not auth_ok:
            print("\n❌ Authentication failed! Please check your API key.")
            return
        
        # Run main tests
        tester.run_basic_tests()
        
        # Show account overview
        tester.analyze_account_data()
        
        print(f"\n✅ Testing completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()