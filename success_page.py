import streamlit as st

def success_page():
    """Display success message and user data."""
    if "user_data" in st.session_state:
        user_data = st.session_state["user_data"]
        st.write(f"Registration Successful!")
        st.write(f"Name: {user_data['name']}")
        st.write(f"Username: {user_data['username']}")
        st.write(f"GitHub Link: {user_data['github_link']}")
    else:
        st.error("No user data found.")
