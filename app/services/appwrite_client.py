from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.account import Account
import os
from dotenv import load_dotenv

load_dotenv()

# Admin client: used for creating users, listing users, etc.
admin_client = Client()
admin_client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
admin_client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
admin_client.set_key(os.getenv("APPWRITE_API_KEY"))

admin_users = Users(admin_client)

# Guest (unauthenticated) client: used for login
guest_client = Client()
guest_client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
guest_client.set_project(os.getenv("APPWRITE_PROJECT_ID"))

guest_account = Account(guest_client)

# Authenticated client with session token
def get_account_client(session_token: str) -> Account:
    user_client = Client()
    user_client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
    user_client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
    user_client.set_session(session_token)
    return Account(user_client)