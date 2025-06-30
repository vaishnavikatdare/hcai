import streamlit as st

from src.ui.ui import ui_page
from src.common.jwt import JWT
from src.ui.login import login_page
from src.ui.sign_up import signup_page

def main():
    st.title("Welcome to the App")

    # Check if the user is logged in
    if "token" in st.session_state and st.session_state["token"]:
        token = st.session_state["token"]
        decoded_token = JWT("random").decode(token)
        if decoded_token:
            ui_page()
            if st.button("Logout"):
                # Clear session state on logout
                st.session_state.clear()
                st.rerun()

    else:
        # Navigation options
        page = st.radio("Choose an option:", ["Login", "Sign Up"], horizontal=True)

        # Render the selected page
        if page == "Login":
            login_page()
        elif page == "Sign Up":
            signup_page()

if __name__ == "__main__":
    main()