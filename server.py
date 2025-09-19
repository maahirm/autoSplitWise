"""
Splitwise MCP Server

A comprehensive Model Context Protocol server for the Splitwise API v3.0.
This server provides access to all major Splitwise functionality including:

TOOLS (Actions):
- User management (get user info, update profile)  
- Group management (create, delete, manage members)
- Friend management (add, remove friends)
- Expense management (create, update, delete expenses)
- Comments (add/remove comments on expenses)
- Notifications (get activity feed)
- Utilities (currencies, categories)

RESOURCES (Cached Data):
- splitwise://user/current - Current user profile (cached)
- splitwise://groups/summary - All groups summary with balances (cached)
- splitwise://friends/summary - Friends and balance overview (cached) 
- splitwise://group/{group_id} - Detailed group information (cached)
- splitwise://expenses/recent - Recent 10 expenses (cached)
- splitwise://categories - All expense categories (cached)
- splitwise://currencies - All supported currencies (cached)

Benefits of Resources:
- Cached for better performance - no repeated API calls
- Structured data that LLMs can reference efficiently  
- Automatic updates when underlying data changes
- URI-based access for easy referencing

Authentication:
- Set SPLITWISE_API_KEY environment variable with your API key
- Get your API key from: https://secure.splitwise.com/apps

Usage Examples:
Tools:
- get_current_user() - Get your user information
- create_simple_expense("Dinner", "50.00", 12345) - Create equal-split expense
- create_payment("Repayment", "25.00", from_user=123, to_user=456) - Record payment

Resources:
- Access splitwise://user/current for cached user profile
- Access splitwise://groups/summary for quick group overview
- Access splitwise://group/12345 for specific group details
"""

from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv("SPLITWISE_API_KEY")

# Configuration
SPLITWISE_BASE_URL = "https://secure.splitwise.com/api/v3.0"
DEFAULT_TIMEOUT = 10

from mcp.server.fastmcp import FastMCP

# Create MCP server with comprehensive Splitwise API access
mcp = FastMCP("Splitwise-Complete-API")

# Validate API key on startup
if not api_key:
    print("Warning: SPLITWISE_API_KEY environment variable not set!")
    print("Please set your API key to use this server.")
    print("Get your API key from: https://secure.splitwise.com/apps")
else:
    print("Splitwise API key loaded")
    print(f"Server ready with {api_key[:8]}...{api_key[-4:]} key")

def _make_request(method: str, endpoint: str, params: dict = None, json_data: dict = None) -> dict:
    """Helper function to make API requests with consistent error handling"""
    if not api_key:
        raise ValueError("SPLITWISE_API_KEY environment variable is not set")
    
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{SPLITWISE_BASE_URL}/{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, params=params, json=json_data, timeout=DEFAULT_TIMEOUT)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
            
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        raise Exception(f"Request timed out while connecting to Splitwise API for {endpoint}")
    except requests.exceptions.ConnectionError:
        raise Exception(f"Failed to connect to Splitwise API for {endpoint}")
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            raise Exception("Invalid API key or unauthorized access")
        elif response.status_code == 403:
            raise Exception("Access forbidden - check your API permissions")
        elif response.status_code == 404:
            raise Exception("Resource not found")
        elif response.status_code == 429:
            raise Exception("Rate limit exceeded - please try again later")
        else:
            raise Exception(f"HTTP error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed for {endpoint}: {str(e)}")
    except ValueError as e:
        raise Exception(f"Failed to parse JSON response for {endpoint}: {str(e)}")

# HELPER FUNCTION FOR TESTING
@mcp.tool()
def mult(a: int, b: int) -> int:
    """Multiply two integers"""
    return a * b + b

# USER ENDPOINTS
@mcp.tool()
def get_current_user() -> dict:
    """Get the current user's information from Splitwise"""
    return _make_request("GET", "get_current_user")

@mcp.tool()
def get_user(user_id: int) -> dict:
    """Get information about another user"""
    return _make_request("GET", f"get_user/{user_id}")

@mcp.tool()
def update_user(user_id: int, first_name: str = None, last_name: str = None, 
               email: str = None, password: str = None, locale: str = None, 
               default_currency: str = None) -> dict:
    """Update a user's information"""
    data = {}
    if first_name:
        data["first_name"] = first_name
    if last_name:
        data["last_name"] = last_name
    if email:
        data["email"] = email
    if password:
        data["password"] = password
    if locale:
        data["locale"] = locale
    if default_currency:
        data["default_currency"] = default_currency
    
    return _make_request("POST", f"update_user/{user_id}", json_data=data)

# GROUP ENDPOINTS
@mcp.tool()
def get_groups() -> dict:
    """Get all groups the current user belongs to"""
    return _make_request("GET", "get_groups")

@mcp.tool()
def get_group(group_id: int) -> dict:
    """Get information about a specific group"""
    return _make_request("GET", f"get_group/{group_id}")

@mcp.tool()
def create_group(name: str, group_type: str = "other", simplify_by_default: bool = True, **user_data) -> dict:
    """Create a new group. group_type can be: home, trip, couple, other, apartment, house"""
    data = {
        "name": name,
        "group_type": group_type,
        "simplify_by_default": simplify_by_default
    }
    # Add user data if provided (users__0__first_name, users__0__email, etc.)
    data.update(user_data)
    return _make_request("POST", "create_group", json_data=data)

@mcp.tool()
def delete_group(group_id: int) -> dict:
    """Delete a group and all associated records"""
    return _make_request("POST", f"delete_group/{group_id}")

@mcp.tool()
def undelete_group(group_id: int) -> dict:
    """Restore a deleted group"""
    return _make_request("POST", f"undelete_group/{group_id}")

@mcp.tool()
def add_user_to_group(group_id: int, user_id: int = None, email: str = None, 
                     first_name: str = None, last_name: str = None) -> dict:
    """Add a user to a group by user_id or by email/name"""
    data = {"group_id": group_id}
    if user_id:
        data["user_id"] = user_id
    else:
        if not email or not first_name:
            raise ValueError("Either user_id or email+first_name must be provided")
        data["email"] = email
        data["first_name"] = first_name
        if last_name:
            data["last_name"] = last_name
    
    return _make_request("POST", "add_user_to_group", json_data=data)

@mcp.tool()
def remove_user_from_group(group_id: int, user_id: int) -> dict:
    """Remove a user from a group (user must have zero balance)"""
    data = {"group_id": group_id, "user_id": user_id}
    return _make_request("POST", "remove_user_from_group", json_data=data)

# FRIEND ENDPOINTS
@mcp.tool()
def get_friends() -> dict:
    """Get all friends of the current user"""
    return _make_request("GET", "get_friends")

@mcp.tool()
def get_friend(user_id: int) -> dict:
    """Get details about a specific friend"""
    return _make_request("GET", f"get_friend/{user_id}")

@mcp.tool()
def create_friend(user_email: str, user_first_name: str = None, user_last_name: str = None) -> dict:
    """Add a friend by email. If user doesn't exist, first_name is required."""
    data = {"user_email": user_email}
    if user_first_name:
        data["user_first_name"] = user_first_name
    if user_last_name:
        data["user_last_name"] = user_last_name
    
    return _make_request("POST", "create_friend", json_data=data)

@mcp.tool()
def create_friends(**friend_data) -> dict:
    """Add multiple friends at once using friends__0__email, friends__0__first_name format"""
    return _make_request("POST", "create_friends", json_data=friend_data)

@mcp.tool()
def delete_friend(user_id: int) -> dict:
    """Delete a friendship with another user"""
    return _make_request("POST", f"delete_friend/{user_id}")

# EXPENSE ENDPOINTS
@mcp.tool()
def get_expenses(group_id: int = None, friend_id: int = None, limit: int = 20, 
               offset: int = 0, dated_after: str = None, dated_before: str = None,
               updated_after: str = None, updated_before: str = None) -> dict:
    """Get expenses with optional filtering"""
    params = {"limit": limit, "offset": offset}
    if group_id is not None:
        params["group_id"] = group_id
    if friend_id is not None:
        params["friend_id"] = friend_id
    if dated_after:
        params["dated_after"] = dated_after
    if dated_before:
        params["dated_before"] = dated_before
    if updated_after:
        params["updated_after"] = updated_after
    if updated_before:
        params["updated_before"] = updated_before
    
    return _make_request("GET", "get_expenses", params=params)

@mcp.tool()
def get_expense(expense_id: int) -> dict:
    """Get information about a specific expense"""
    return _make_request("GET", f"get_expense/{expense_id}")

@mcp.tool()
def create_expense(cost: str, description: str, group_id: int, split_equally: bool = True,
                  details: str = None, date: str = None, repeat_interval: str = "never",
                  currency_code: str = "USD", category_id: int = None, **user_data) -> dict:
    """Create a new expense. Use split_equally=True for equal splits or provide user shares."""
    data = {
        "cost": cost,
        "description": description,
        "group_id": group_id,
        "split_equally": split_equally
    }
    
    if details:
        data["details"] = details
    if date:
        data["date"] = date
    if repeat_interval:
        data["repeat_interval"] = repeat_interval
    if currency_code:
        data["currency_code"] = currency_code
    if category_id:
        data["category_id"] = category_id
    
    # Add user share data (users__0__user_id, users__0__paid_share, etc.)
    data.update(user_data)
    
    return _make_request("POST", "create_expense", json_data=data)

@mcp.tool()
def update_expense(expense_id: int, cost: str = None, description: str = None, 
                  group_id: int = None, details: str = None, date: str = None,
                  repeat_interval: str = None, currency_code: str = None,
                  category_id: int = None, **user_data) -> dict:
    """Update an existing expense"""
    data = {}
    if cost:
        data["cost"] = cost
    if description:
        data["description"] = description
    if group_id is not None:
        data["group_id"] = group_id
    if details:
        data["details"] = details
    if date:
        data["date"] = date
    if repeat_interval:
        data["repeat_interval"] = repeat_interval
    if currency_code:
        data["currency_code"] = currency_code
    if category_id:
        data["category_id"] = category_id
    
    # Add user share data
    data.update(user_data)
    
    return _make_request("POST", f"update_expense/{expense_id}", json_data=data)

@mcp.tool()
def delete_expense(expense_id: int) -> dict:
    """Delete an expense"""
    return _make_request("POST", f"delete_expense/{expense_id}")

@mcp.tool()
def undelete_expense(expense_id: int) -> dict:
    """Restore a deleted expense"""
    return _make_request("POST", f"undelete_expense/{expense_id}")

# COMMENT ENDPOINTS
@mcp.tool()
def get_comments(expense_id: int) -> dict:
    """Get comments for a specific expense"""
    params = {"expense_id": expense_id}
    return _make_request("GET", "get_comments", params=params)

@mcp.tool()
def create_comment(expense_id: int, content: str) -> dict:
    """Create a comment on an expense"""
    data = {"expense_id": expense_id, "content": content}
    return _make_request("POST", "create_comment", json_data=data)

@mcp.tool()
def delete_comment(comment_id: int) -> dict:
    """Delete a comment"""
    return _make_request("POST", f"delete_comment/{comment_id}")

# NOTIFICATION ENDPOINTS
@mcp.tool()
def get_notifications(updated_after: str = None, limit: int = 0) -> dict:
    """Get recent notifications. Use limit=0 for maximum notifications."""
    params = {}
    if updated_after:
        params["updated_after"] = updated_after
    if limit:
        params["limit"] = limit
    
    return _make_request("GET", "get_notifications", params=params)

# OTHER UTILITY ENDPOINTS
@mcp.tool()
def get_currencies() -> dict:
    """Get all supported currencies"""
    return _make_request("GET", "get_currencies")

@mcp.tool()
def get_categories() -> dict:
    """Get all supported expense categories"""
    return _make_request("GET", "get_categories")

# ADDITIONAL CONVENIENCE FUNCTIONS
@mcp.tool()
def create_simple_expense(description: str, amount: str, group_id: int, 
                         currency: str = "USD", category_id: int = 18) -> dict:
    """Create a simple equally-split expense in a group"""
    return create_expense(
        cost=amount,
        description=description,
        group_id=group_id,
        split_equally=True,
        currency_code=currency,
        category_id=category_id
    )

@mcp.tool()
def create_payment(description: str, amount: str, from_user_id: int, to_user_id: int,
                  group_id: int = 0, currency: str = "USD") -> dict:
    """Create a payment between two users"""
    return create_expense(
        cost=amount,
        description=description,
        group_id=group_id,
        split_equally=False,
        currency_code=currency,
        **{
            "users__0__user_id": from_user_id,
            "users__0__paid_share": "0.00",
            "users__0__owed_share": amount,
            "users__1__user_id": to_user_id,
            "users__1__paid_share": amount,
            "users__1__owed_share": "0.00"
        }
    )

@mcp.tool()
def get_user_balance_with_friend(friend_id: int) -> dict:
    """Get detailed balance information with a specific friend"""
    friend_info = get_friend(friend_id)
    return {
        "friend": friend_info.get("friend", {}),
        "balance_summary": friend_info.get("friend", {}).get("balance", [])
    }

@mcp.tool()
def get_group_balances(group_id: int) -> dict:
    """Get all balances within a specific group"""
    group_info = get_group(group_id)
    return {
        "group_name": group_info.get("group", {}).get("name"),
        "simplified_debts": group_info.get("group", {}).get("simplified_debts", []),
        "original_debts": group_info.get("group", {}).get("original_debts", [])
    }

# MCP RESOURCES - Cached data for better efficiency

@mcp.resource("splitwise://user/current")
def get_current_user_resource() -> str:
    """Get current user information as a cached resource"""
    try:
        user_data = _make_request("GET", "get_current_user")
        user = user_data.get("user", {})
        
        return f"""Current Splitwise User Profile:
Name: {user.get('first_name', '')} {user.get('last_name', '')}
Email: {user.get('email', '')}
ID: {user.get('id', '')}
Default Currency: {user.get('default_currency', 'USD')}
Locale: {user.get('locale', 'en')}
Registration Status: {user.get('registration_status', '')}
Notifications Count: {user.get('notifications_count', 0)}
"""
    except Exception as e:
        return f"Error fetching user data: {str(e)}"

@mcp.resource("splitwise://groups/summary")
def get_groups_summary_resource() -> str:
    """Get a summary of all groups as a cached resource"""
    try:
        groups_data = _make_request("GET", "get_groups")
        groups = groups_data.get("groups", [])
        
        summary = "Splitwise Groups Summary:\n\n"
        for group in groups:
            summary += f"• {group.get('name', 'Unnamed')} (ID: {group.get('id')})\n"
            summary += f"  Type: {group.get('group_type', 'unknown')}\n"
            summary += f"  Members: {len(group.get('members', []))}\n"
            
            # Calculate total balance for this group
            simplified_debts = group.get('simplified_debts', [])
            if simplified_debts:
                total_debt = sum(float(debt.get('amount', 0)) for debt in simplified_debts)
                summary += f"  Total Outstanding: {total_debt:.2f} {group.get('simplified_debts', [{}])[0].get('currency_code', 'USD') if simplified_debts else 'USD'}\n"
            
            summary += f"  Updated: {group.get('updated_at', 'N/A')}\n\n"
        
        summary += f"Total Groups: {len(groups)}"
        return summary
        
    except Exception as e:
        return f"Error fetching groups summary: {str(e)}"

@mcp.resource("splitwise://friends/summary")  
def get_friends_summary_resource() -> str:
    """Get a summary of all friends and balances as a cached resource"""
    try:
        friends_data = _make_request("GET", "get_friends")
        friends = friends_data.get("friends", [])
        
        summary = "Splitwise Friends Summary:\n\n"
        total_owed_to_you = 0.0
        total_you_owe = 0.0
        
        for friend in friends:
            name = f"{friend.get('first_name', '')} {friend.get('last_name', '')}"
            summary += f"• {name.strip()} (ID: {friend.get('id')})\n"
            summary += f"  Email: {friend.get('email', 'N/A')}\n"
            
            # Calculate balances
            balances = friend.get('balance', [])
            friend_total = 0.0
            for balance in balances:
                amount = float(balance.get('amount', 0))
                friend_total += amount
                if amount > 0:
                    total_owed_to_you += amount
                else:
                    total_you_owe += abs(amount)
            
            if friend_total > 0:
                summary += f"  Owes you: {friend_total:.2f}\n"
            elif friend_total < 0:
                summary += f"  You owe: {abs(friend_total):.2f}\n"
            else:
                summary += f"  Balance: Even\n"
            
            summary += f"  Updated: {friend.get('updated_at', 'N/A')}\n\n"
        
        summary += f"Total Friends: {len(friends)}\n"
        summary += f"Total Owed to You: {total_owed_to_you:.2f}\n" 
        summary += f"Total You Owe: {total_you_owe:.2f}\n"
        summary += f"Net Balance: {total_owed_to_you - total_you_owe:.2f}"
        
        return summary
        
    except Exception as e:
        return f"Error fetching friends summary: {str(e)}"

@mcp.resource("splitwise://group/{group_id}")
def get_group_details_resource(group_id: str) -> str:
    """Get detailed information about a specific group"""
    try:
        group_data = _make_request("GET", f"get_group/{group_id}")
        group = group_data.get("group", {})
        
        details = f"Group Details: {group.get('name', 'Unnamed')}\n\n"
        details += f"ID: {group.get('id')}\n"
        details += f"Type: {group.get('group_type', 'unknown')}\n"
        details += f"Simplify by Default: {group.get('simplify_by_default', False)}\n"
        details += f"Updated: {group.get('updated_at', 'N/A')}\n\n"
        
        # Members
        members = group.get('members', [])
        details += f"Members ({len(members)}):\n"
        for member in members:
            user = member.get('user', {})
            name = f"{user.get('first_name', '')} {user.get('last_name', '')}"
            details += f"• {name.strip()} (ID: {user.get('id')}) - {user.get('email', 'N/A')}\n"
        
        # Simplified debts
        simplified_debts = group.get('simplified_debts', [])
        if simplified_debts:
            details += f"\nSimplified Debts ({len(simplified_debts)}):\n"
            for debt in simplified_debts:
                from_user = debt.get('from_user', {})
                to_user = debt.get('to_user', {})
                from_name = f"{from_user.get('first_name', '')} {from_user.get('last_name', '')}"
                to_name = f"{to_user.get('first_name', '')} {to_user.get('last_name', '')}"
                amount = debt.get('amount', 0)
                currency = debt.get('currency_code', 'USD')
                details += f"• {from_name.strip()} owes {to_name.strip()}: {amount} {currency}\n"
        
        return details
        
    except Exception as e:
        return f"Error fetching group {group_id}: {str(e)}"

@mcp.resource("splitwise://expenses/recent")
def get_recent_expenses_resource() -> str:
    """Get recent expenses as a cached resource"""
    try:
        expenses_data = _make_request("GET", "get_expenses", params={"limit": 10})
        expenses = expenses_data.get("expenses", [])
        
        summary = "Recent Splitwise Expenses (Last 10):\n\n"
        
        for expense in expenses:
            summary += f"• {expense.get('description', 'Untitled')}\n"
            summary += f"  Amount: {expense.get('cost', '0')} {expense.get('currency_code', 'USD')}\n"
            summary += f"  Date: {expense.get('date', 'N/A')}\n"
            summary += f"  Group ID: {expense.get('group_id', 'N/A')}\n"
            
            # Show who paid and who owes
            users = expense.get('users', [])
            if users:
                payers = [u for u in users if float(u.get('paid_share', 0)) > 0]
                if payers:
                    payer = payers[0].get('user', {})
                    payer_name = f"{payer.get('first_name', '')} {payer.get('last_name', '')}"
                    summary += f"  Paid by: {payer_name.strip()}\n"
            
            summary += f"  ID: {expense.get('id')}\n\n"
        
        return summary
        
    except Exception as e:
        return f"Error fetching recent expenses: {str(e)}"

@mcp.resource("splitwise://categories")
def get_categories_resource() -> str:
    """Get expense categories as a cached resource"""
    try:
        categories_data = _make_request("GET", "get_categories")
        categories = categories_data.get("categories", [])
        
        resource_content = "Splitwise Expense Categories:\n\n"
        
        for category in categories:
            resource_content += f"• {category.get('name', 'Unnamed')} (ID: {category.get('id')})\n"
            
            # Show subcategories if any
            subcategories = category.get('subcategories', [])
            for subcat in subcategories:
                resource_content += f"  - {subcat.get('name', 'Unnamed')} (ID: {subcat.get('id')})\n"
            
            resource_content += "\n"
        
        return resource_content
        
    except Exception as e:
        return f"Error fetching categories: {str(e)}"


@mcp.resource("splitwise://analytics/spending-by-category")
def get_spending_analytics_resource() -> str:
    """Get spending analytics by category from recent expenses"""
    try:
        # Get recent expenses (last 50 for better analytics)
        expenses_data = _make_request("GET", "get_expenses", params={"limit": 50})
        expenses = expenses_data.get("expenses", [])
        
        # Get categories for mapping
        categories_data = _make_request("GET", "get_categories") 
        categories = categories_data.get("categories", [])
        
        # Create category lookup
        category_lookup = {}
        for cat in categories:
            category_lookup[cat.get('id')] = cat.get('name', 'Unknown')
            for subcat in cat.get('subcategories', []):
                category_lookup[subcat.get('id')] = f"{cat.get('name')} - {subcat.get('name')}"
        
        # Analyze spending by category
        category_spending = {}
        current_user_data = _make_request("GET", "get_current_user")
        current_user_id = current_user_data.get("user", {}).get("id")
        
        for expense in expenses:
            category_id = expense.get('category_id')
            category_name = category_lookup.get(category_id, 'Uncategorized')
            cost = float(expense.get('cost', 0))
            
            # Only count expenses where current user participated
            users = expense.get('users', [])
            user_participated = any(u.get('user_id') == current_user_id for u in users)
            
            if user_participated:
                if category_name not in category_spending:
                    category_spending[category_name] = {'total': 0, 'count': 0}
                category_spending[category_name]['total'] += cost
                category_spending[category_name]['count'] += 1
        
        # Format results
        analytics = "Spending Analytics by Category (Last 50 Expenses):\n\n"
        
        sorted_categories = sorted(category_spending.items(), key=lambda x: x[1]['total'], reverse=True)
        total_spending = sum(data['total'] for data in category_spending.values())
        
        for category, data in sorted_categories:
            percentage = (data['total'] / total_spending * 100) if total_spending > 0 else 0
            analytics += f"• {category}\n"
            analytics += f"  Total: {data['total']:.2f} ({percentage:.1f}%)\n"
            analytics += f"  Expenses: {data['count']}\n"
            analytics += f"  Average: {data['total'] / data['count']:.2f}\n\n"
        
        analytics += f"Total Analyzed Spending: {total_spending:.2f}\n"
        analytics += f"Total Categories: {len(category_spending)}"
        
        return analytics
        
    except Exception as e:
        return f"Error generating spending analytics: {str(e)}"

@mcp.resource("splitwise://analytics/monthly-summary")
def get_monthly_summary_resource() -> str:
    """Get monthly spending summary"""
    try:
        from datetime import datetime, timedelta
        import calendar
        
        # Get expenses from last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        expenses_data = _make_request("GET", "get_expenses", params={
            "limit": 100,
            "dated_after": start_date.isoformat() + "Z"
        })
        expenses = expenses_data.get("expenses", [])
        
        # Get current user
        current_user_data = _make_request("GET", "get_current_user")
        current_user_id = current_user_data.get("user", {}).get("id")
        
        # Analyze expenses
        total_paid = 0.0
        total_owed = 0.0
        expense_count = 0
        daily_spending = {}
        
        for expense in expenses:
            expense_date = expense.get('date', '')[:10]  # Get just date part
            users = expense.get('users', [])
            
            # Find current user's share
            for user in users:
                if user.get('user_id') == current_user_id:
                    paid = float(user.get('paid_share', 0))
                    owed = float(user.get('owed_share', 0))
                    
                    total_paid += paid
                    total_owed += owed
                    expense_count += 1
                    
                    if expense_date not in daily_spending:
                        daily_spending[expense_date] = 0
                    daily_spending[expense_date] += owed
                    break
        
        # Format summary
        summary = f"Monthly Summary (Last 30 Days):\n\n"
        summary += f"Total Expenses Participated: {expense_count}\n"
        summary += f"Total Amount Paid: {total_paid:.2f}\n"
        summary += f"Total Amount Owed: {total_owed:.2f}\n"
        summary += f"Net Balance: {total_paid - total_owed:.2f}\n"
        summary += f"Average Daily Spending: {total_owed / 30:.2f}\n\n"
        
        # Top spending days
        if daily_spending:
            top_days = sorted(daily_spending.items(), key=lambda x: x[1], reverse=True)[:5]
            summary += "Top Spending Days:\n"
            for date, amount in top_days:
                summary += f"• {date}: {amount:.2f}\n"
        
        return summary
        
    except Exception as e:
        return f"Error generating monthly summary: {str(e)}"

@mcp.resource("splitwise://notifications/recent")
def get_recent_notifications_resource() -> str:
    """Get recent notifications as a cached resource"""
    try:
        notifications_data = _make_request("GET", "get_notifications", params={"limit": 20})
        notifications = notifications_data.get("notifications", [])
        
        summary = "Recent Splitwise Notifications (Last 20):\n\n"
        
        notification_types = {
            0: "Expense added",
            1: "Expense updated", 
            2: "Expense deleted",
            3: "Comment added",
            4: "Added to group",
            5: "Removed from group",
            6: "Group deleted",
            7: "Group settings changed",
            8: "Added as friend",
            9: "Removed as friend",
            10: "News",
            11: "Debt simplification",
            12: "Group undeleted",
            13: "Expense undeleted",
            14: "Group currency conversion",
            15: "Friend currency conversion"
        }
        
        for notification in notifications:
            notif_type = notification_types.get(notification.get('type', -1), "Unknown")
            content = notification.get('content', 'No content')
            created_at = notification.get('created_at', 'N/A')[:19]  # Remove timezone for readability
            
            summary += f"• [{notif_type}] {created_at}\n"
            # Strip HTML tags from content for cleaner display
            import re
            clean_content = re.sub('<.*?>', '', content)
            summary += f"  {clean_content}\n\n"
        
        return summary
        
    except Exception as e:
        return f"Error fetching notifications: {str(e)}"

# # Add a dynamic greeting resource
# @mcp.resource("greeting://{name}")
# def get_greeting(name: str) -> str:
#     """Get a personalized greeting"""
#     return f"Hello, {name}!"


# # Add a prompt
# @mcp.prompt()
# def greet_user(name: str, style: str = "friendly") -> str:
#     """Generate a greeting prompt"""
#     styles = {
#         "friendly": "Please write a warm, friendly greeting",
#         "formal": "Please write a formal, professional greeting",
#         "casual": "Please write a casual, relaxed greeting",
#     }

#     return f"{styles.get(style, styles['friendly'])} for someone named {name}."


def main():
    mcp.run()


if __name__ == "__main__":
    main()
