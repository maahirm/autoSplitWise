#!/usr/bin/env python3
"""
Quick Splitwise API Demo

This script demonstrates how to use the Splitwise API tester
and shows what you can expect when testing the APIs.
"""

from tests.testAPIs import SplitwiseAPITester
import json

def demo_without_api_key():
    """Demonstrate what happens without a proper API key"""
    print("🎯 Demo: Testing without API key")
    print("=" * 50)
    
    try:
        # This will show what happens when no API key is provided
        tester = SplitwiseAPITester()  # No API key
    except ValueError as e:
        print(f"❌ Expected error: {e}")
        print("\n✅ This is the expected behavior when no API key is provided.")
        return False
    
    return True

def demo_with_fake_api_key():
    """Demonstrate what happens with a fake API key"""
    print("\n🎯 Demo: Testing with fake API key")
    print("=" * 50)
    
    # Use a fake API key to see authentication errors
    fake_tester = SplitwiseAPITester("fake_api_key_for_demo")
    
    # Try to get current user (will fail with 401 Unauthorized)
    print("\n🧪 Testing GET /get_current_user with fake key...")
    response = fake_tester.test_get_current_user()
    
    if not response['success'] or response.get('status_code') == 401:
        print("✅ Got expected authentication error")
        return True
    else:
        print("❓ Unexpected response")
        return False

def demo_api_structure():
    """Show the structure of how to use the API"""
    print("\n🎯 Demo: API Usage Structure")
    print("=" * 50)
    
    print("""
📝 How to use the Splitwise API Tester:

1️⃣ Get your API key:
   - Go to https://secure.splitwise.com/
   - Navigate to Account Settings → API Keys
   - Generate a new API key

2️⃣ Set up environment:
   - Copy .env.example to .env
   - Add your API key: SPLITWISE_API_KEY=your_actual_key

3️⃣ Initialize the tester:
   ```python
   from testAPIs import SplitwiseAPITester
   tester = SplitwiseAPITester()  # Reads from .env
   # OR
   tester = SplitwiseAPITester("your_api_key")  # Direct key
   ```

4️⃣ Run tests:
   ```python
   # Run all basic tests
   tester.run_basic_tests()
   
   # Test specific endpoints
   user_info = tester.test_get_current_user()
   groups = tester.test_get_groups()
   friends = tester.test_get_friends()
   expenses = tester.test_get_expenses(limit=10)
   
   # Analyze your account
   tester.analyze_account_data()
   ```

5️⃣ Create new data:
   ```python
   # Create a group
   new_group = tester.test_create_group("My Test Group", "trip")
   
   # Add a friend  
   new_friend = tester.test_create_friend(
       email="friend@example.com",
       first_name="Test", 
       last_name="Friend"
   )
   
   # Create an expense
   new_expense = tester.test_create_expense(
       cost="25.50",
       description="Test dinner",
       group_id=0  # 0 for no group
   )
   ```
""")

def show_available_endpoints():
    """Show all available API endpoints"""
    print("\n🎯 Available Splitwise API Endpoints")
    print("=" * 50)
    
    endpoints = {
        "User Management": [
            "GET /get_current_user - Get your user information",
            "GET /get_user/{id} - Get another user's information",
            "POST /update_user/{id} - Update user information"
        ],
        "Group Management": [
            "GET /get_groups - List all your groups",
            "GET /get_group/{id} - Get specific group details",
            "POST /create_group - Create a new group",
            "POST /delete_group/{id} - Delete a group",
            "POST /add_user_to_group - Add user to group",
            "POST /remove_user_from_group - Remove user from group"
        ],
        "Friend Management": [
            "GET /get_friends - List all your friends",
            "GET /get_friend/{id} - Get specific friend details",
            "POST /create_friend - Add a new friend",
            "POST /create_friends - Add multiple friends",
            "POST /delete_friend/{id} - Remove a friend"
        ],
        "Expense Management": [
            "GET /get_expenses - List expenses with filters",
            "GET /get_expense/{id} - Get specific expense details",
            "POST /create_expense - Create a new expense",
            "POST /update_expense/{id} - Update an expense",
            "POST /delete_expense/{id} - Delete an expense"
        ],
        "Comments": [
            "GET /get_comments - Get expense comments", 
            "POST /create_comment - Add a comment",
            "POST /delete_comment/{id} - Delete a comment"
        ],
        "Notifications": [
            "GET /get_notifications - Get recent notifications"
        ],
        "Utility": [
            "GET /get_currencies - Get supported currencies",
            "GET /get_categories - Get expense categories"
        ]
    }
    
    for category, endpoint_list in endpoints.items():
        print(f"\n📁 {category}:")
        for endpoint in endpoint_list:
            print(f"   • {endpoint}")

def main():
    """Run the demo"""
    print("🎬 Splitwise API Demo")
    print("=" * 50)
    print("This demo shows you how the Splitwise API testing works")
    print("and what to expect when you set up your own API key.")
    
    # Demo 1: No API key
    demo_without_api_key()
    
    # Demo 2: Fake API key  
    demo_with_fake_api_key()
    
    # Demo 3: Show how to use the API
    demo_api_structure()
    
    # Demo 4: Show available endpoints
    show_available_endpoints()
    
    print(f"\n{'=' * 50}")
    print("🎯 Next Steps:")
    print("1. Get your Splitwise API key")
    print("2. Set up your .env file")
    print("3. Run: python testAPIs.py")
    print("4. Start building your Splitwise application!")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    main()
