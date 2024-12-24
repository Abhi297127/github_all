import streamlit as st

def success_page():
    st.title("Registration Successful 🎉")
    
    # Check if user data is in session state
    if "user_data" in st.session_state:
        user_data = st.session_state["user_data"]
        st.write("Registered User Data:")
        st.json(user_data)
    else:
        st.error("No user data found in session state!")
