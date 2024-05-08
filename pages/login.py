import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

# Initialize the Firebase app
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Create a Firebase Auth object
auth = auth.Client()

# Create a session state object to store the user's login status
session_state = st.session_state

# Create a login form
email = st.text_input("Email")
password = st.text_input("Password", type="password")
submit_button = st.button("Login")

# Handle the login button click
if submit_button:
    try:
        # Sign in with the provided email and password
        user = auth.sign_in_with_email_and_password(email, password)

        # If the login is successful, set the user's login status to True
        session_state.logged_in = True
    except auth.EmailNotFoundError:
        # If the email is not found, display an error message
        st.error("Email not found.")
    except auth.InvalidPasswordError:
        # If the password is invalid, display an error message
        st.error("Invalid password.")
    except auth.Error:
        # If there is any other error, display an error message
        st.error("An error occurred. Please try again.")

# Display the login status
if session_state.logged_in:
    st.success("Logged in successfully!")

    # Display the authenticated member page
    st.write("This is the authenticated member page.")
else:
    st.info("Please log in to continue.")

