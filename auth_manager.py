# Import necessary modules for JSON handling, OS operations, and hashing
import json
import os
import hashlib

# Constants for login configuration
LOGIN_FILE = "login_config.json"

DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password123"

# Function to hash passwords using SHA256
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# Function to save user credentials to file
def save_credentials(username: str, password: str):
    with open(LOGIN_FILE, "w") as file:
        json.dump(
            {
                "username": username,
                "password_hash": hash_password(password)
            },
            file,
            indent=4
        )

# Function to load credentials from file, creating defaults if not exist
def load_credentials():
    if not os.path.exists(LOGIN_FILE):
        save_credentials(DEFAULT_USERNAME, DEFAULT_PASSWORD)

    with open(LOGIN_FILE, "r") as file:
        return json.load(file)

# Function to validate user login
def validate_login(username: str, password: str) -> bool:
    creds = load_credentials()
    return (
        username == creds["username"]
        and hash_password(password) == creds["password_hash"]
    )

# Function to change user password
def change_password(current_password: str, new_password: str):
    creds = load_credentials()

    if hash_password(current_password) != creds["password_hash"]:
        return False, "Current password is incorrect."

    save_credentials(creds["username"], new_password)
    return True, "Password changed successfully."