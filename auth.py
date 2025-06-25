import streamlit as st
import os
from dotenv import load_dotenv
import hashlib
from streamlit_cookies_controller import CookieController
from datetime import datetime, timedelta
import secrets

# Load environment variables
load_dotenv()

# Initialize cookie controller
cookie_controller = CookieController()

def check_password():
    """Returns `True` if the user had the correct password."""
    
    # Check if authenticated via cookie
    auth_cookie = cookie_controller.get("auth_token")
    if auth_cookie:
        # Verify cookie is valid (simple check - in production use JWT or similar)
        expected_token = hashlib.sha256(
            f"{os.getenv('APP_PASSWORD', 'admin123')}:{os.getenv('COOKIE_SECRET', 'default_secret')}".encode()
        ).hexdigest()
        
        if auth_cookie == expected_token:
            st.session_state["password_correct"] = True
            return True

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        entered_password = st.session_state["password"]
        correct_password = os.getenv("APP_PASSWORD", "admin123")  # Default password if not set
        
        if entered_password == correct_password:
            st.session_state["password_correct"] = True
            
            # Set authentication cookie
            auth_token = hashlib.sha256(
                f"{correct_password}:{os.getenv('COOKIE_SECRET', 'default_secret')}".encode()
            ).hexdigest()
            
            # Cookie expires in 7 days
            cookie_controller.set("auth_token", auth_token, max_age=7*24*60*60)
            
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run or logout
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        # Show login form
        st.markdown("## 🔐 Authentication Required")
        st.markdown("Please enter the password to access this application.")
        
        # Password input
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password",
            help="Contact administrator for password"
        )
        
        if "password_correct" in st.session_state and st.session_state["password_correct"] == False:
            st.error("😕 Password incorrect. Please try again.")
        
        return False
    
    else:
        return True

def logout():
    """Logout function to clear session state"""
    if st.button("🚪 Logout", help="Click to logout"):
        st.session_state["password_correct"] = False
        # Remove authentication cookie
        cookie_controller.remove("auth_token")
        st.rerun()

def show_logout_button():
    """Show logout button in sidebar"""
    with st.sidebar:
        st.markdown("---")
        logout()