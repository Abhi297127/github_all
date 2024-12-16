import streamlit as st
from pymongo import MongoClient
import admin
import student
import os

# MongoDB Connection
username = os.getenv("MONGO_USER", "abhishelke297127")
password = os.getenv("MONGO_PASS", "Abhi%402971")
connection_string = f"mongodb+srv://{username}:{password}@cluster0.uu8yq.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client.Question  # Database name

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Login functionality
def login():
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    # Dummy user credentials
    USERS = {
        "admin": {"password": "admin123", "role": "admin"},
        "student1": {"password": "student123", "role": "student"},
        "student2": {"password": "student456", "role": "student"},
    }

    if st.button("Login", key="login_button"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]
            st.session_state.username = username
            st.success(f"Welcome {username}! You are logged in as {USERS[username]['role'].capitalize()}.")
            st.session_state.current_page = "Home"
            st.rerun()
        else:
            st.error("Invalid username or password")

# Logout functionality
def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.current_page = "Home"
    st.rerun()

# Sidebar toolbar
def toolbar():
    st.sidebar.title("Home Dashboard")

    # Sidebar options based on login state and role
    if st.session_state.logged_in:
        if st.session_state.role == "admin":
            options = ["Home", "Admin Dashboard"]
        elif st.session_state.role == "student":
            options = ["Home", "Student Dashboard"]
    else:
        options = ["Home", "Login"]

    # Update current page
    selected_option = st.sidebar.radio("Go to:", options, key="sidebar_navigation")
    st.session_state.current_page = selected_option

# Header with logout button
def header():
    cols = st.columns([5, 1])  # Adjust column widths
    with cols[0]:
        st.subheader("Login successfully")
    with cols[1]:
        if st.session_state.logged_in:
            st.markdown(f"**{st.session_state.username}**")
            if st.button("Logout", key="logout_button"):
                logout()

# Home page content
def homepage():
    st.title("Welcome to the Portal")
    
    # Show different content based on login state
    if st.session_state.logged_in:
        st.write(f"Hello, **{st.session_state.username}**! You are logged in as **{st.session_state.role.capitalize()}**.")
        st.write("Use the sidebar to navigate to your dashboard.")
    else:
        st.write("This is the public homepage. Please log in to access your dashboard.")

# Main function
def main():
    header()  # Show header with logout button if logged in
    toolbar()  # Show navigation options based on role

    # Render content based on the current page
    if st.session_state.current_page == "Home":
        homepage()
    elif st.session_state.current_page == "Login":
        login()
    elif st.session_state.current_page == "Admin Dashboard" and st.session_state.role == "admin":
        admin.admin_dashboard(db)
    elif st.session_state.current_page == "Student Dashboard" and st.session_state.role == "student":
        student.student_dashboard(db)

if __name__ == "__main__":
    main()
