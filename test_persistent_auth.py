#!/usr/bin/env python3
"""
Test persistent login functionality locally
"""
import streamlit as st
from auth_manager import AuthManager
import os
import tempfile

def test_persistent_auth():
    print("=== Testing Persistent Authentication ===")
    
    # Clear any existing session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Test authentication manager initialization
    try:
        auth_manager = AuthManager()
        print("✅ AuthManager initialized successfully")
    except Exception as e:
        print(f"❌ AuthManager initialization failed: {e}")
        return
    
    # Test authentication check without login
    print("\n1. Testing initial authentication check...")
    is_auth_initial = auth_manager.is_authenticated()
    print(f"Initial authentication status: {is_auth_initial}")
    
    # Test persistent login check
    print("\n2. Testing persistent login check...")
    persistent_login = auth_manager.check_persistent_login()
    print(f"Persistent login status: {persistent_login}")
    
    # Check session state
    print(f"\n3. Session State:")
    print(f"  authentication_status: {st.session_state.get('authentication_status')}")
    print(f"  username: {st.session_state.get('username')}")
    print(f"  name: {st.session_state.get('name')}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_persistent_auth()
