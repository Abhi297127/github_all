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

def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

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
            st.success(f"Welcome {username}!")
            st.session_state.current_page = "Home"
            st.rerun()
        else:
            st.error("Invalid username or password")

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.current_page = "Home"
    st.rerun()

def toolbar():
    st.sidebar.title("Navigation")

    # Sidebar navigation options
    if st.session_state.logged_in:
        options = ["Home"]
        if st.session_state.role == "admin":
            options.append("Admin Dashboard")
        elif st.session_state.role == "student":
            options.append("Student Dashboard")
    else:
        options = ["Home", "Login"]

    # Sidebar navigation
    selected_option = st.sidebar.radio("Go to:", options, key="sidebar_navigation")

    if selected_option == "Home":
        st.session_state.current_page = "Home"
    elif selected_option == "Login":
        st.session_state.current_page = "Login"
    elif selected_option == "Admin Dashboard" and st.session_state.logged_in:
        st.session_state.current_page = "Admin Dashboard"
    elif selected_option == "Student Dashboard" and st.session_state.logged_in:
        st.session_state.current_page = "Student Dashboard"

def header():
    cols = st.columns([8, 1])  # Adjust column width ratio
    with cols[0]:
        st.write("")  # Placeholder for alignment
    with cols[1]:
        if st.session_state.logged_in:
            if st.button("Logout", key="logout_button"):
                logout()

def homepage():
    st.title("Welcome to the Homepage")
    st.write("This is the Home page of the application.")
    st.write("Navigate to other sections using the sidebar.")

def main():
    header()
    toolbar()

    if st.session_state.current_page == "Home":
        homepage()
    elif st.session_state.current_page == "Login":
        login()
    elif st.session_state.current_page == "Admin Dashboard" and st.session_state.logged_in:
        admin.admin_dashboard(db)
    elif st.session_state.current_page == "Student Dashboard" and st.session_state.logged_in:
        student.student_dashboard(db)

if __name__ == "__main__":
    main()
