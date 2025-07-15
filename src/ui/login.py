import streamlit as st

from src.common.user import User

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            # Store the logged-in user in session state
            user = User()
            token = user.authenticate(username, password)
            if not token:
                st.error("Invalid username or password. Please check and try again.")
                return
            st.session_state["token"] = token
            st.session_state["username"] = username
            st.write(st.session_state)
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Please fill both the fields!")