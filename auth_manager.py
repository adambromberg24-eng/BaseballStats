import streamlit as st
import streamlit_authenticator as stauth
import yaml
from typing import Optional, Tuple

class AuthManager:
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        
        # Initialize authenticator with updated API (removing deprecated preauthorized parameter)
        try:
            self.authenticator = stauth.Authenticate(
                self.config['credentials'],
                self.config['cookie']['name'],
                self.config['cookie']['key'],
                self.config['cookie']['expiry_days']
                # Removed preauthorized parameter due to deprecation
            )
            print("DEBUG: Authenticator initialized successfully")
        except Exception as e:
            print(f"DEBUG: Error initializing authenticator with new API: {e}")
            # Fallback to older API if needed
            try:
                self.authenticator = stauth.Authenticate(
                    self.config['credentials'],
                    self.config['cookie']['name'],
                    self.config['cookie']['key'],
                    self.config['cookie']['expiry_days'],
                    self.config.get('preauthorized', {})
                )
                print("DEBUG: Authenticator initialized with fallback API")
            except Exception as fallback_error:
                print(f"DEBUG: Fallback also failed: {fallback_error}")
                raise fallback_error
        
        # Don't auto-check authentication on initialization to avoid form display issues
        # This will be called explicitly when needed

    def _load_config(self) -> dict:
        with open(self.config_file, 'r') as file:
            return yaml.safe_load(file)

    def _save_config(self):
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False)

    def _check_authentication(self):
        """Check for existing authentication cookies and restore session"""
        try:
            # Skip if we already have a valid session
            if st.session_state.get('authentication_status') is True and st.session_state.get('username'):
                print(f"DEBUG: Already authenticated: {st.session_state.get('username')}")
                return
                
            print("DEBUG: Checking for persistent authentication...")
            
            # Try to initialize authentication without triggering login form
            # The authenticator should automatically check cookies on initialization
            if hasattr(self.authenticator, 'authentication_status'):
                auth_status = self.authenticator.authentication_status
                username = getattr(self.authenticator, 'username', None) or st.session_state.get('username')
                name = getattr(self.authenticator, 'name', None) or st.session_state.get('name')
                
                print(f"DEBUG: Authenticator status: {auth_status}, username: {username}")
                
                if auth_status is True and username:
                    # User is authenticated via cookie
                    st.session_state['authentication_status'] = True
                    st.session_state['name'] = name or username
                    st.session_state['username'] = username
                    print(f"DEBUG: Auto-authenticated user from cookie: {username}")
                    return
            
            # Fallback - check session state directly
            auth_status = st.session_state.get('authentication_status')
            username = st.session_state.get('username')
            name = st.session_state.get('name')
            
            if auth_status is True and username:
                print(f"DEBUG: Found existing session: {username}")
            else:
                print("DEBUG: No valid authentication found")
                st.session_state['authentication_status'] = None
                
        except Exception as e:
            print(f"DEBUG: Error checking authentication: {e}")
            st.session_state['authentication_status'] = None

    def login(self) -> Tuple[bool, Optional[str]]:
        """Display login form and return (success, username)"""
        try:
            # If already authenticated, don't show login form
            if self.is_authenticated():
                return True, self.get_current_user()
            
            # Only show login form when explicitly called and user is not authenticated
            try:
                # Use the authenticator login method which handles the form display
                result = self.authenticator.login(location='main')
                
                # Handle the result based on what the API returns
                if isinstance(result, tuple):
                    if len(result) == 3:
                        name, authentication_status, username = result
                    elif len(result) == 2:
                        authentication_status, username = result
                        name = username
                    else:
                        authentication_status = result[0] if result else None
                        username = st.session_state.get('username')
                        name = st.session_state.get('name')
                else:
                    # Single value or None
                    authentication_status = result
                    username = st.session_state.get('username')
                    name = st.session_state.get('name')
                        
            except Exception as e:
                print(f"DEBUG: Login method error: {e}")
                # Fallback to session state
                authentication_status = st.session_state.get('authentication_status')
                username = st.session_state.get('username')
                name = st.session_state.get('name')
            
            if authentication_status is True:
                print(f"DEBUG: User logged in successfully: {username}")
                return True, username
            elif authentication_status is False:
                print(f"DEBUG: Login failed")
                return False, username
            else:
                # No login attempt yet (form is displayed but not submitted)
                return None, None
                
        except Exception as e:
            print(f"DEBUG: Error in login: {e}")
            return False, None

    def logout(self, location='sidebar'):
        """Logout the current user"""
        if self.is_authenticated():
            try:
                # Try the newer API
                self.authenticator.logout(location=location)
            except TypeError:
                # Fallback for older API
                try:
                    self.authenticator.logout('Logout', location)
                except Exception as e:
                    print(f"DEBUG: Logout fallback failed: {e}")
                    
            # Clear session state manually to ensure logout
            for key in ['authentication_status', 'name', 'username']:
                if key in st.session_state:
                    del st.session_state[key]
            print("DEBUG: User logged out successfully")

    def register_user(self, username: str, name: str, password: str, email: str) -> bool:
        """Register a new user"""
        if username in self.config['credentials']['usernames']:
            return False  # User already exists

        # Hash the password
        hashed_password = stauth.Hasher([password]).generate()[0]

        # Add user to config
        self.config['credentials']['usernames'][username] = {
            'name': name,
            'password': hashed_password,
            'email': email
        }

        # Save updated config (removed preauthorized email handling as it's deprecated)
        self._save_config()
        print(f"DEBUG: Successfully registered new user: {username}")
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
    
    def check_persistent_login(self) -> bool:
        """Check for persistent login without showing any forms"""
        try:
            # Force a re-check of authentication status from cookies
            self._check_authentication()
            return self.is_authenticated()
        except Exception as e:
            print(f"DEBUG: Error checking persistent login: {e}")
            return False
