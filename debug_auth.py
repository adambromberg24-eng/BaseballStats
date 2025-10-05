#!/usr/bin/env python3

import streamlit as st
import streamlit_authenticator as stauth
import yaml
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

def test_cookie_persistence():
    """Test script to debug cookie persistence issues"""
    
    print("=== DEBUGGING STREAMLIT AUTHENTICATOR COOKIE PERSISTENCE ===")
    
    # Load config
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    print(f"Config loaded: {config['cookie']}")
    
    # Initialize authenticator
    try:
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )
        print("✅ Authenticator initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing authenticator: {e}")
        return
    
    # Check initial state
    print(f"\nInitial session state:")
    print(f"  authentication_status: {st.session_state.get('authentication_status')}")
    print(f"  username: {st.session_state.get('username')}")
    print(f"  name: {st.session_state.get('name')}")
    
    # Try to check for existing authentication
    print(f"\nTrying to check for existing authentication...")
    
    try:
        # This should check cookies and restore session if valid
        result = authenticator.login(location='main')
        print(f"Login call result: {result}")
        
        print(f"\nAfter login call:")
        print(f"  authentication_status: {st.session_state.get('authentication_status')}")
        print(f"  username: {st.session_state.get('username')}")
        print(f"  name: {st.session_state.get('name')}")
        
        # Check authenticator attributes
        print(f"\nAuthenticator attributes:")
        for attr in ['authentication_status', 'username', 'name']:
            if hasattr(authenticator, attr):
                value = getattr(authenticator, attr)
                print(f"  {attr}: {value}")
        
    except Exception as e:
        print(f"❌ Error during login call: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("This is a debugging script for Streamlit authentication.")
    print("Run this with: streamlit run debug_auth.py")
    print("\nTo test manually:")
    print("1. First login to your app")
    print("2. Then run this script to see if cookies persist")
    
    # Initialize Streamlit
    st.title("Authentication Debug Tool")
    
    if st.button("Test Cookie Persistence"):
        test_cookie_persistence()
