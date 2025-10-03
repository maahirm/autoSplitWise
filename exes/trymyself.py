import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("SPLITWISE_API_KEY")

friend_data = {
    "friend_id": 70395038
}

response = requests.get(
    "https://secure.splitwise.com/api/v3.0/get_expenses",
    headers={"Authorization": f"Bearer {api_key}"},
    json=friend_data,
    timeout=10
)

# update_data = {
#     "user_email": "ada@example.com",
#     "user_first_name": "Ada",
#     "user_last_name": "Denvers"
# }

# response = requests.post(
#     "https://secure.splitwise.com/api/v3.0/delete_friend/816000",
#     headers={"Authorization": f"Bearer {api_key}"},
#     json=update_data,  # Use json parameter for JSON data
#     timeout=10
# )

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}")
    print(response.text)
