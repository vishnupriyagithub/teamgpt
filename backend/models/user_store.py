import json
import os

USERS_FILE = "data/users.json"
os.makedirs("data", exist_ok=True)

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def get_or_create_user(user):
    users = load_users()
    if user["user_id"] not in users:
        users[user["user_id"]] = user
        save_users(users)
    return users[user["user_id"]]
