#!/usr/bin/env python3

"""
Minimal working example based on streamlit-authenticator documentation
to test persistent authentication properly.
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml

def main():
    st.set_page_config(page_title="Auth Test", layout="wide")
    st.title("🔐 Persistent Authentication Test (v0.4.2)")
    
    # Load config
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    # Initialize authenticator for v0.4.2
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    # CRITICAL: Call login() - this checks cookies and handles authentication
    try:
        result = authenticator.login()
        
        # Get auth info from session state
        name = st.session_state.get('name')
        authentication_status = st.session_state.get('authentication_status')
        username = st.session_state.get('username')
        
        st.write("### Debug Info:")
        st.write(f"Login result: {result}")
        st.write(f"Name: {name}")
        st.write(f"Authentication Status: {authentication_status}")
        st.write(f"Username: {username}")
        
        if authentication_status == False:
            st.error('❌ Username/password is incorrect')
        elif authentication_status == None:
            st.warning('⏳ Please enter your username and password')
        elif authentication_status:
            # User is authenticated
            st.success(f'🎉 Welcome {name}!')
            st.balloons()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Test Refresh"):
                    st.rerun()
            with col2:
                if st.button("� Logout"):
                    authenticator.logout()
                    st.rerun()
            
            st.info("💡 **Test Instructions:** Refresh this page - you should remain logged in!")
            
    except Exception as e:
        st.error(f"❌ Error: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
