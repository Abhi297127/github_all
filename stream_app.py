import streamlit as st

# Title for the application
st.title("Login Page")

# Role selection
role = st.selectbox("Select Role", ["Admin", "Student"])

# Input fields for login
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Login button
if st.button("Login"):
    if role == "Admin":
        if username == "admin" and password == "adminpass":
            st.success("Welcome, Admin!")
            # Redirect or show admin-specific content here
        else:
            st.error("Invalid Admin credentials")
    elif role == "Student":
        if username == "student" and password == "studentpass":
            st.success("Welcome, Student!")
            # Redirect or show student-specific content here
        else:
            st.error("Invalid Student credentials")
