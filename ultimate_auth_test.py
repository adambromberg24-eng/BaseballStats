#!/usr/bin/env python3

"""
Ultimate authentication test - let's figure out exactly how v0.4.2 works
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml

def main():
    st.set_page_config(page_title="Ultimate Auth Test", layout="wide")
    st.title("🔬 Ultimate Authentication Test v0.4.2 - OFFICIAL PATTERN")
    
    # Load config
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    # Initialize authenticator exactly like the docs
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    st.write("### Official Pattern from streamlit-authenticator docs:")
    st.code("""
    # This is the EXACT pattern from the official docs
    try:
        authenticator.login()
    except Exception as e:
        st.error(e)
    
    if st.session_state.get('authentication_status'):
        # User is authenticated
    elif st.session_state.get('authentication_status') is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get('authentication_status') is None:
        st.warning('Please enter your username and password')
    """)
    
    # THE OFFICIAL PATTERN - call login() every time
    try:
        authenticator.login()
        st.write("✅ authenticator.login() called successfully")
    except Exception as e:
        st.error(f"❌ Error calling login(): {e}")
        return
    
    # Check session state exactly like the docs
    auth_status = st.session_state.get('authentication_status')
    username = st.session_state.get('username')
    name = st.session_state.get('name')
    
    st.write("### Session State After login():")
    st.json({
        'authentication_status': auth_status,
        'username': username,
        'name': name
    })
    
    # Handle authentication exactly like the docs
    if auth_status:
        # User is authenticated
        st.success(f"🎉 Welcome {name}!")
        
        # Show logout button
        authenticator.logout()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Test Refresh - Should Stay Logged In"):
                st.rerun()
        with col2:
            st.info("� Refresh this page - you should remain logged in due to cookies!")
                
    elif auth_status is False:
        st.error('❌ Username/password is incorrect')
        
    elif auth_status is None:
        st.warning('⏳ Please enter your username and password')
        st.info("👆 The login form should be visible above")

if __name__ == "__main__":
    main()
