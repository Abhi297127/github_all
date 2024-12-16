import streamlit as st
from pymongo import MongoClient
import os

# MongoDB Connection
username = "abhishelke297127"
password = "Abhi%402971"
connection_string = f"mongodb+srv://{username}:{password}@cluster0.uu8yq.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(connection_string)
    db = client.Question  # Database name
except Exception as e:
    st.error(f"Error connecting to MongoDB: {e}")
    db = None

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# User credentials (dummy data)
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "AF0315573": {"password": "Mad123", "role": "Madhuri_Shinde"},
    # Add more users here...
}

# Login functionality
def login():
    st.title("Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        username = username.strip()
        password = password.strip()

        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]
            st.session_state.username = username
            st.success(f"Welcome {username}! You are logged in as {USERS[username]['role']}.")
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
    st.sidebar.title("Navigation")

    if st.session_state.logged_in:
        if st.session_state.role == "admin":
            options = ["Home", "Admin Dashboard"]
        else:
            options = ["Home", "Student Dashboard"]
    else:
        options = ["Home", "Login"]

    selected_option = st.sidebar.radio("Go to:", options, key="sidebar_navigation")
    st.session_state.current_page = selected_option

# Header with logout button
def header():
    cols = st.columns([4, 1])  # Adjust column widths
    with cols[0]:
        st.subheader("Welcome to the Portal")
    with cols[1]:
        if st.session_state.logged_in:
            st.markdown(f"**{st.session_state.username}**")
            if st.button("Logout", key="logout_button"):
                logout()

# Home page content
def homepage():
    st.title("Home Page")

    if st.session_state.logged_in:
        st.write(f"Hello, **{st.session_state.username}**! You are logged in as **{st.session_state.role}**.")
        st.write("Use the sidebar to navigate to your dashboard.")
    else:
        st.write("This is the public homepage. Please log in to access your dashboard.")

# Admin Dashboard
def admin_dashboard(db):
    st.title("Admin Dashboard")
    st.write("Welcome to the Admin Dashboard.")
    if db:
        st.write("Connected to MongoDB.")
        st.write(db.list_collection_names())
    else:
        st.error("Database connection not available.")

# Student Dashboard
def student_dashboard(db):
    st.title("Student Dashboard")
    st.write("Welcome to the Student Dashboard.")
    if db:
        st.write("Connected to MongoDB.")
        st.write("Collections available:")
        st.write(db.list_collection_names())
    else:
        st.error("Database connection not available.")

# Main function
def main():
    header()  # Show header with logout button if logged in
    toolbar()  # Show navigation options based on role

    if st.session_state.current_page == "Home":
        homepage()
    elif st.session_state.current_page == "Login":
        login()
    elif st.session_state.current_page == "Admin Dashboard" and st.session_state.role == "admin":
        admin_dashboard(db)
    elif st.session_state.current_page == "Student Dashboard":
        student_dashboard(db)
    else:
        st.error("Page not found or access restricted.")

if __name__ == "__main__":
    main()
