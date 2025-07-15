import streamlit as st

from src.common.user import User
from src.constants.defaults import HEIGHT, WEIGHT
from src.custom_types.user import UserModel

def signup_page():
    st.title("Sign Up")

    # Input fields
    st.markdown("Sign up to create your own meal plans.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    weight = st.number_input(
        label=WEIGHT["message"],
        min_value=WEIGHT["min"],
        max_value=WEIGHT["max"],
        step=WEIGHT["step"]
    )
    height = height = st.number_input(
        label=HEIGHT["message"],
        min_value=HEIGHT["min"],
        max_value=HEIGHT["max"],
        step=HEIGHT["step"]
    )
    diet_preference = st.radio(
        "Diet Preference", 
        options=["veg", "non-veg"], 
        format_func=lambda x: "Vegetarian" if x == "veg" else "Non-Vegetarian", 
        horizontal=True
    )

    # Submit button
    if st.button("Sign Up"):
        if username and password and first_name and last_name:
            user = User()
            createUser = UserModel(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                weight=weight,
                height=height,
                diet_preference=diet_preference
            )
            registration = user.register(createUser)
            if not registration:
                st.error("Username already exists. Please choose a different username.")
                return
            st.success("Account created successful!")
            st.write(f"Welcome, {createUser.first_name} {createUser.last_name}!")
        else:
            st.error("Please fill in all required fields.")
