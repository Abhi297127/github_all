import streamlit as st

def success_page():
    """Display the success page based on query parameters."""
    query_params = st.query_params  # Retrieve the current query parameters
    page = query_params.get("page", "default")  # Get the "page" parameter
    
    if page == "success":
        st.title("Registration Successful 🎉")
        st.write("Your registration was successful!")

        # Optionally show user data stored in session state
        if "user_data" in st.session_state:
            st.write("Registered Details:")
            st.json(st.session_state["user_data"])
    else:
        st.error("Invalid page parameter!")
