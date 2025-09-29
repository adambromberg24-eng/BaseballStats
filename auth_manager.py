import streamlit as st
import streamlit_authenticator as stauth
import yaml
from typing import Optional, Tuple

class AuthManager:
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        
        # Initialize authenticator with proper cookie settings
        self.authenticator = stauth.Authenticate(
            self.config['credentials'],
            self.config['cookie']['name'],
            self.config['cookie']['key'],
            self.config['cookie']['expiry_days'],
            self.config.get('preauthorized', {})
        )
        
        # Auto-check authentication status on initialization
        self._check_authentication()

    def _load_config(self) -> dict:
        with open(self.config_file, 'r') as file:
            return yaml.safe_load(file)

    def _save_config(self):
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False)

    def _check_authentication(self):
        """Check for existing authentication cookies and restore session"""
        try:
            # This will check for existing authentication cookies
            # Handle different versions of streamlit-authenticator
            try:
                result = self.authenticator.login('main')
                if isinstance(result, tuple) and len(result) == 3:
                    name, authentication_status, username = result
                else:
                    # Fallback for different API versions
                    authentication_status = st.session_state.get('authentication_status')
                    username = st.session_state.get('username')
                    name = st.session_state.get('name')
            except Exception as auth_error:
                print(f"DEBUG: Authentication check error: {auth_error}")
                # Try to get from session state directly
                authentication_status = st.session_state.get('authentication_status')
                username = st.session_state.get('username')
                name = st.session_state.get('name')
            
            if authentication_status is True and username:
                # User is authenticated via cookie
                st.session_state['authentication_status'] = True
                st.session_state['name'] = name
                st.session_state['username'] = username
                print(f"DEBUG: Auto-authenticated user from cookie: {username}")
            elif authentication_status is False:
                # Failed authentication
                st.session_state['authentication_status'] = False
                print("DEBUG: Authentication failed or expired")
            else:
                # No authentication attempt yet
                st.session_state['authentication_status'] = None
                print("DEBUG: No authentication cookie found")
                
        except Exception as e:
            print(f"DEBUG: Error checking authentication: {e}")
            st.session_state['authentication_status'] = None

    def login(self) -> Tuple[bool, Optional[str]]:
        """Display login form and return (success, username)"""
        try:
            # Only show login form if not already authenticated
            if not self.is_authenticated():
                name, authentication_status, username = self.authenticator.login('main', 'Login')
                
                if authentication_status is True:
                    print(f"DEBUG: User logged in successfully: {username}")
                    return True, username
                elif authentication_status is False:
                    print(f"DEBUG: Login failed for username: {username}")
                    return False, username
                else:
                    # No login attempt yet
                    return None, None
            else:
                # Already authenticated
                return True, self.get_current_user()
        except Exception as e:
            print(f"DEBUG: Error in login: {e}")
            return False, None

    def logout(self, location='sidebar'):
        """Logout the current user"""
        if self.is_authenticated():
            self.authenticator.logout('Logout', location)
            # Clear session state
            for key in ['authentication_status', 'name', 'username']:
                if key in st.session_state:
                    del st.session_state[key]
            print("DEBUG: User logged out successfully")

    def register_user(self, username: str, name: str, password: str, email: str) -> bool:
        """Register a new user"""
        if username in self.config['credentials']['usernames']:
            return False  # User already exists

        # Hash the password
        hashed_password = stauth.Hasher.hash(password)

        # Add user to config
        self.config['credentials']['usernames'][username] = {
            'name': name,
            'password': hashed_password,
            'email': email
        }

        # Add to preauthorized if needed
        if email not in self.config.get('preauthorized', {}).get('emails', []):
            self.config.setdefault('preauthorized', {}).setdefault('emails', []).append(email)

        self._save_config()
        return True

    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        auth_status = st.session_state.get('authentication_status', None)
        username = st.session_state.get('username', None)
        
        # True if authenticated and has username
        is_auth = auth_status is True and username is not None
        
        if is_auth:
            print(f"DEBUG: User is authenticated: {username}")
        else:
            print(f"DEBUG: User not authenticated. Status: {auth_status}, Username: {username}")
            
        return is_auth

    def get_current_user(self) -> Optional[str]:
        """Get current username"""
        username = st.session_state.get('username')
        if username:
            print(f"DEBUG: Current user: {username}")
        return username

    def get_user_display_name(self) -> Optional[str]:
        """Get current user's display name"""
        return st.session_state.get('name')
