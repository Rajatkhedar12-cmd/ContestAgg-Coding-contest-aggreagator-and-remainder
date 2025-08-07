import bcrypt
import streamlit as st
from utils.db import users_col

# Hash plain-text password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Check password against stored hash
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Register a new user
from utils.db import users_col

def register_user(username, password, email):
    if users_col.find_one({"username": username}):
        st.error("Username already exists.")
    elif users_col.find_one({"email": email}):
        st.error("Email already registered.")
    else:
        users_col.insert_one({
            "username": username,
            "password": password,
            "email": email
        })
        st.success("User registered successfully!")


# Login an existing user
def login_user(username, password):
    user = users_col.find_one({"username": username, "password": password})
    if user:
        st.session_state["user"] = {
            "username": user["username"],
            "email": user.get("email")
        }
        return True
    else:
        st.error("Invalid username or password.")
        return False

