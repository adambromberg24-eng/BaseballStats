#!/usr/bin/env python3
"""
Test persistent authentication functionality
"""
import streamlit as st
from auth_manager import AuthManager

def test_persistent_auth():
    print("=== Testing Persistent Authentication ===")
    
    # Initialize auth manager
    auth_manager = AuthManager()
    
    # Check authentication status
    is_auth = auth_manager.is_authenticated()
    current_user = auth_manager.get_current_user()
    user_display = auth_manager.get_user_display_name()
    
    print(f"Authentication Status: {is_auth}")
    print(f"Current User: {current_user}")
    print(f"Display Name: {user_display}")
    
    # Check session state
    print(f"\nSession State:")
    print(f"  authentication_status: {st.session_state.get('authentication_status')}")
    print(f"  username: {st.session_state.get('username')}")
    print(f"  name: {st.session_state.get('name')}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    # This won't work exactly like in Streamlit, but we can test the logic
    test_persistent_auth()
