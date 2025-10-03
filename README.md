# Splitwise API Tester

A comprehensive Python application for testing and exploring the Splitwise API. This tool helps you understand how the Splitwise API works by testing all major endpoints and providing detailed response analysis.

## Features

- 🔐 **Authentication Testing** - Verify your API key works
- 👤 **User Management** - Get current user info and other user details
- 👥 **Group Operations** - List, create, and manage groups
- 👫 **Friend Management** - View and add friends
- 💰 **Expense Tracking** - Create, view, and manage expenses
- 🔔 **Notifications** - Check recent activity
- 📊 **Account Analysis** - Get an overview of your Splitwise account
- 🛠️ **Utility Functions** - Get currencies and expense categories

## Setup

1. **Install Dependencies**
   ```bash
   pip install requests python-dotenv tabulate
   ```

2. **Get Your Splitwise API Key**
   - Log into [Splitwise](https://secure.splitwise.com/)
   - Go to Account Settings → API Keys
   - Generate a new API key

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

4. **Run the Tester**
   ```bash
   python testAPIs.py
   ```

## API Endpoints Tested

### User Endpoints
- `GET /get_current_user` - Get current user information
- `GET /get_user/{id}` - Get another user's information

### Group Endpoints  
- `GET /get_groups` - List all groups
- `GET /get_group/{id}` - Get specific group details
- `POST /create_group` - Create a new group

### Friend Endpoints
- `GET /get_friends` - List all friends
- `GET /get_friend/{id}` - Get specific friend details
- `POST /create_friend` - Add a new friend

### Expense Endpoints
- `GET /get_expenses` - List expenses with filters
- `GET /get_expense/{id}` - Get specific expense details  
- `POST /create_expense` - Create a new expense

### Other Endpoints
- `GET /get_notifications` - Get recent notifications
- `GET /get_currencies` - Get supported currencies
- `GET /get_categories` - Get expense categories

## Usage Examples

### Basic Testing
```python
from testAPIs import SplitwiseAPITester

# Initialize with your API key
tester = SplitwiseAPITester("your_api_key_here")

# Run all basic tests
tester.run_basic_tests()

# Analyze your account
tester.analyze_account_data()
```

### Individual Tests
```python
# Test specific endpoints
user_info = tester.test_get_current_user()
groups = tester.test_get_groups()
expenses = tester.test_get_expenses(limit=10)
```

### Create New Data
```python
# Create a test group
new_group = tester.test_create_group("Test Group", "trip")

# Create a test expense  
new_expense = tester.test_create_expense("25.50", "Dinner", group_id=0)
```

## Understanding the Output

The script provides detailed output for each API call:

- ✅ **Success indicators** - Shows if the API call worked
- 📊 **Response data** - Full JSON responses from the API
- ❌ **Error handling** - Clear error messages for troubleshooting
- 📈 **Summary tables** - Overview of test results

## API Authentication

The Splitwise API uses OAuth 2.0 Bearer tokens. This script uses your API key as a Bearer token:

```
Authorization: Bearer your_api_key_here
```

## Rate Limits

Be aware that Splitwise has rate limits on their API. This script is designed for testing and development use. For production applications, implement proper rate limiting and error handling.

## API Documentation

For complete API documentation, visit: https://dev.splitwise.com/

## Terms of Use

This tool is for testing and development purposes. Please review Splitwise's API Terms of Use before building production applications.

## Troubleshooting

### Common Issues

1. **Authentication Error (401)**
   - Check your API key is correct
   - Ensure the key hasn't expired
   - Verify you copied the full key without extra spaces

2. **Forbidden Error (403)**  
   - Your API key might not have the required permissions
   - Some operations require specific account types

3. **Not Found Error (404)**
   - Check that user/group/expense IDs exist
   - Ensure you have access to the requested resource

4. **Rate Limited (429)**
   - Wait a few moments before retrying
   - Implement delays between requests for production use

### Getting Help

- Check the [Splitwise API Documentation](https://dev.splitwise.com/)
- Review the [API Terms of Use](https://dev.splitwise.com/#section/Terms-of-Use)
- Contact Splitwise support for API-specific issues

## License

This testing tool is provided for educational and development purposes. Please respect Splitwise's terms of service when using their API.
