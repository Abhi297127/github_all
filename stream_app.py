import streamlit as st

# Mock credentials for demonstration
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "student1": {"password": "student123", "role": "student"},
    "student2": {"password": "student456", "role": "student"},
}

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

def login():
    st.title("Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]
            st.session_state.username = username
            st.success(f"Welcome {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def admin_page():
    st.title("Admin Dashboard")
    st.write("Welcome to the admin dashboard!")
    # Add admin-specific functionality here
    if st.button("Logout"):
        logout()

def student_page():
    st.title("Student Dashboard")
    st.write(f"Welcome {st.session_state.username}!")
    # Add student-specific functionality here
    if st.button("Logout"):
        logout()

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.rerun()

# Main logic
if st.session_state.logged_in:
    if st.session_state.role == "admin":
        admin_page()
    elif st.session_state.role == "student":
        student_page()
else:
    login()
