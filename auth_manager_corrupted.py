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
            # Use the authenticator login method
            name, authentication_status, username = self.authenticator.login('Login', 'main')
            
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
            self.authenticator.logout('Logout', 'sidebar')
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
                return False, None
            
            # Get results from session state
            auth_status = st.session_state.get('authentication_status')
            username = st.session_state.get('username')
            name = st.session_state.get('name')
            
            print(f"DEBUG: Login results - auth: {auth_status}, user: {username}, name: {name}")
            
            if auth_status is True:
                print(f"DEBUG: ✅ Login successful: {username}")
                return True, username
            elif auth_status is False:
                print("DEBUG: ❌ Login failed")
                return False, username  
            else:
                print("DEBUG: ℹ️ Login form displayed, waiting for input")
                return None, None
                
        except Exception as e:
            print(f"DEBUG: ❌ Error in login: {e}")
            import traceback
            traceback.print_exc()
            return False, None

    def logout(self, location='sidebar'):
        """Logout using streamlit-authenticator v0.4.2"""
        if self.is_authenticated():
            try:
                # In v0.4.2, logout() doesn't take parameters
                self.authenticator.logout()
                print("DEBUG: ✅ User logged out successfully")
            except Exception as e:
                print(f"DEBUG: ❌ Logout error: {e}")
                # Manual cleanup as fallback
                for key in ['authentication_status', 'name', 'username']:
                    if key in st.session_state:
                        del st.session_state[key]

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
        """Check for persistent login using streamlit-authenticator v0.4.2"""
        try:
            print("DEBUG: Checking persistent login with v0.4.2...")
            
            # In v0.4.2, we MUST call login() to check cookies
            # It doesn't return anything, just updates session state
            try:
                self.authenticator.login()
                print("DEBUG: ✅ login() called successfully")
            except Exception as e:
                print(f"DEBUG: ❌ Error calling login(): {e}")
                return False
            
            # Check session state for authentication results
            auth_status = st.session_state.get('authentication_status')
            username = st.session_state.get('username') 
            name = st.session_state.get('name')
            
            print(f"DEBUG: Session state after login() call:")
            print(f"  authentication_status: {auth_status}")
            print(f"  username: {username}")
            print(f"  name: {name}")
            
            # Return True if user is authenticated
            if auth_status is True and username:
                print(f"DEBUG: ✅ User authenticated: {username}")
                return True
            elif auth_status is False:
                print("DEBUG: ❌ Authentication failed")
                return False
            else:
                print("DEBUG: ℹ️ No authentication (new session)")
                return False
                
        except Exception as e:
            print(f"DEBUG: ❌ Error in check_persistent_login: {e}")
            import traceback
            traceback.print_exc()
            return False
