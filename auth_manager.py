import streamlit as st
import streamlit_authenticator as stauth
import yaml
from typing import Optional, Tuple

class AuthManager:
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()
        
        # Initialize authenticator 
        self.authenticator = stauth.Authenticate(
            self.config['credentials'],
            self.config['cookie']['name'], 
            self.config['cookie']['key'],
            self.config['cookie']['expiry_days']
        )

    def _load_config(self) -> dict:
        with open(self.config_file, 'r') as file:
            return yaml.safe_load(file)

    def _save_config(self):
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False)

    def check_authentication(self) -> bool:
        """Check if user is currently authenticated"""
        auth_status = st.session_state.get('authentication_status')
        return auth_status is True

    def login(self) -> Tuple[Optional[bool], Optional[str]]:
        """Handle user login"""
        try:
            # For streamlit-authenticator 0.4.2 - login() doesn't return values, just updates session state
            self.authenticator.login()
            
            # Get authentication status from session state
            authentication_status = st.session_state.get('authentication_status')
            username = st.session_state.get('username')
            
            if authentication_status is True:
                return True, username
            elif authentication_status is False:
                return False, None
            else:
                return None, None
                
        except Exception as e:
            st.error(f"Login error: {e}")
            return False, None

    def logout(self):
        """Handle user logout"""
        try:
            # For streamlit-authenticator 0.4.2 - no parameters needed
            self.authenticator.logout()
            st.session_state['authentication_status'] = None
            st.session_state['username'] = None
            st.session_state['name'] = None
        except Exception as e:
            st.error(f"Logout error: {e}")

    def get_current_user(self) -> Optional[str]:
        """Get the current authenticated user"""
        if self.check_authentication():
            return st.session_state.get('username')
        return None

    def get_user_display_name(self) -> Optional[str]:
        """Get the display name of the current user"""
        if self.check_authentication():
            return st.session_state.get('name')
        return None

    def register_user(self, username: str, name: str, password: str, email: str) -> bool:
        """Register a new user"""
        try:
            # Check if username already exists
            if username in self.config['credentials']['usernames']:
                return False
            
            # Hash the password
            hashed_password = stauth.Hasher([password]).generate()[0]
            
            # Add new user to config
            self.config['credentials']['usernames'][username] = {
                'name': name,
                'password': hashed_password,
                'email': email
            }
            
            # Save config
            self._save_config()
            return True
            
        except Exception as e:
            st.error(f"Registration error: {e}")
            return False

    def update_user_profile(self, username: str, name: str = None, email: str = None) -> bool:
        """Update user profile information (name and email)"""
        try:
            if username not in self.config['credentials']['usernames']:
                return False
            
            # Update name if provided
            if name is not None:
                self.config['credentials']['usernames'][username]['name'] = name
                # Update session state if this is the current user
                if st.session_state.get('username') == username:
                    st.session_state['name'] = name
            
            # Update email if provided
            if email is not None:
                self.config['credentials']['usernames'][username]['email'] = email
            
            # Save config
            self._save_config()
            return True
            
        except Exception as e:
            st.error(f"Profile update error: {e}")
            return False

    def change_password(self, username: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            if username not in self.config['credentials']['usernames']:
                return False
            
            # Verify current password
            stored_password = self.config['credentials']['usernames'][username]['password']
            if not stauth.Hasher([current_password]).check([stored_password])[0]:
                return False
            
            # Hash new password
            hashed_new_password = stauth.Hasher([new_password]).generate()[0]
            
            # Update password
            self.config['credentials']['usernames'][username]['password'] = hashed_new_password
            
            # Save config
            self._save_config()
            return True
            
        except Exception as e:
            st.error(f"Password change error: {e}")
            return False

    def get_user_info(self, username: str) -> Optional[dict]:
        """Get user information"""
        try:
            if username in self.config['credentials']['usernames']:
                user_data = self.config['credentials']['usernames'][username].copy()
                # Don't return the password
                user_data.pop('password', None)
                return user_data
            return None
        except Exception as e:
            st.error(f"Error getting user info: {e}")
            return None