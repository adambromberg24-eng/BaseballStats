#!/usr/bin/env python3

"""
Simple test app to understand streamlit-authenticator cookie behavior
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml

st.set_page_config(page_title="Auth Test", layout="wide")

def main():
    st.title("🧪 Authentication Cookie Test")
    
    # Load config
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
    except Exception as e:
        st.error(f"Error loading config: {e}")
        return
    
    # Initialize authenticator
    try:
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )
        st.success("✅ Authenticator initialized")
    except Exception as e:
        st.error(f"Error initializing authenticator: {e}")
        return
    
    # Display current session state
    st.markdown("### 📊 Current Session State:")
    st.json({
        "authentication_status": st.session_state.get('authentication_status'),
        "username": st.session_state.get('username'),
        "name": st.session_state.get('name'),
    })
    
    # Check if user is already authenticated
    auth_status = st.session_state.get('authentication_status')
    
    if auth_status is True:
        st.success(f"🎉 You are logged in as: {st.session_state.get('name')} ({st.session_state.get('username')})")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh Page"):
                st.rerun()
        with col2:
            if st.button("🚪 Logout"):
                authenticator.logout(location='main')
                st.rerun()
    else:
        st.info("🔐 Please log in to test persistent authentication")
        
        # Show login form
        result = authenticator.login(location='main')
        
        st.markdown("### 🔧 Login Result:")
        st.write(f"Result: {result}")
        st.write(f"Session after login attempt:")
        st.json({
            "authentication_status": st.session_state.get('authentication_status'),
            "username": st.session_state.get('username'),
            "name": st.session_state.get('name'),
        })
        
        # If login successful, refresh
        if st.session_state.get('authentication_status') is True:
            st.success("✅ Login successful! Refreshing...")
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 Instructions:")
    st.markdown("""
    1. **First time**: Log in with your credentials
    2. **After login**: Notice you're authenticated 
    3. **Test persistence**: Click 'Refresh Page' or refresh browser
    4. **Expected**: You should remain logged in after refresh
    """)

if __name__ == "__main__":
    main()
