import streamlit as st

def success_page():
    st.title("Registration Successful 🎉")
    
    # Retrieve user data from query parameters
    user_data = st.experimental_get_query_params().get("user_data", [None])[0]
    
    if user_data:
        # Parse the user data from the query params
        name, username, github_link = user_data.split(",")
        st.write(f"Name: {name}")
        st.write(f"Username: {username}")
        st.write(f"GitHub Link: {github_link}")
    else:
        st.error("No user data found in the query parameters.")
