import streamlit as st

def success_page():
    """Show success page."""
    st.title("Registration Successful 🎉")
    st.write("Your registration was successful!")

    if "user_data" in st.session_state:
        st.write("Registered Details:")
        st.json(st.session_state["user_data"])

    st.button("Login", on_click=lambda: st.query_params(page="login"))
