import streamlit as st
from pymongo import MongoClient
from urllib.parse import urlparse
from admin import admin_dashboard, manage_students, manage_questions
from student import student_dashboard, student_assignments, student_data
from github import Github

# MongoDB Connection
username = "abhishelke297127"
password = "Abhi%402971"
connection_string = f"mongodb+srv://{username}:{password}@cluster0.uu8yq.mongodb.net/?retryWrites=true&w=majority"

def connect_to_mongo():
    try:
        client = MongoClient(connection_string)
        db = client.Question  # Database name
        return db
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {e}")
        return None

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Login functionality
def login():
    """Log in an existing user."""
    client = MongoClient(connection_string)
    # Access the specific databases
    login_db = client["LoginData"]
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login_db.users.find_one({"username": username, "password": password})
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["name"] = user["name"]  # Store full name
            st.session_state["role"] = user["role"]  # Assign role
            st.success(f"Welcome {user['name']}!")
        else:
            st.error("Invalid Username or Password")



def extract_owner_repo(github_url):
    """Extract owner and repository name from GitHub URL."""
    github_url = github_url.rstrip(".git")
    parsed_url = urlparse(github_url)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]
    return None, None

def register_user():
    """Register a new user."""
    st.title("Register")
    name = st.text_input("Name")
    username = st.text_input("Username")
    github_link = st.text_input("GitHub Repository Link")
    github_token = st.text_input("GitHub Token")
    password = None
    client = MongoClient(connection_string)
    # Access the specific databases
    login_db = client["LoginData"]

    if github_link:
        owner, repo = extract_owner_repo(github_link)
        if owner and repo:
            try:
                # Validate GitHub token
                g = Github(github_token)
                user = g.get_user()
                st.write("GitHub token is valid")
            except Exception as e:
                st.error("Invalid GitHub token")
                return
            st.success("GitHub Repository is Public")
            password = st.text_input("Set Password", type="password")

    if st.button("Submit"):
        if login_db["users"].find_one({"username": username}) or login_db["users"].find_one({"github_link": github_link}):
            st.error("Username or GitHub link already exists")
        else:
            # Redirect to success page
            st.session_state["registration_success"] = True
            st.session_state["user_data"] = {
                "name": name,
                "username": username,
                "github_link": github_link,
                "github_token": github_token,
            }
            st.query_params.page = "success"
            # Add user to database
            st.info("Please navigate to the login page to access your account")
            login_db["users"].insert_one({"name": name, "username": username, "github_link": github_link, "password": password, "github_token": github_token, "role": "student"})
            st.success("Registration successful")



# Logout functionality
def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.current_page = "Home"
    st.rerun()

# Sidebar toolbar with dynamic options
def toolbar():
    st.sidebar.title("Navigation")

    if st.session_state.logged_in:
        if st.session_state.role == "admin":
            admin_options = [
                "Home", 
                "Manage Questions", 
                "Student Codes", 
                "Admin Dashboard"
            ]
            selected_option = st.sidebar.radio("Admin Options:", admin_options, key="admin_sidebar")
        else:
            student_options = [
                "Home", 
                "My Assignments", 
                "Student Dashboard", 
                "My Data"
            ]
            selected_option = st.sidebar.radio("Student Options:", student_options, key="student_sidebar")
    else:
        selected_option = st.sidebar.radio("Go to:", ["Home", "Login","Register"])

    st.session_state.current_page = selected_option

# Header with logout button (remains the same)
def header():
    cols = st.columns([4, 1])
    with cols[0]:
        st.subheader("Welcome to the Portal")
    with cols[1]:
        if st.session_state.logged_in:
            st.markdown(f"**{st.session_state.username}**")
            if st.button("Logout", key="logout_button"):
                logout()

# Homepage (remains the same)
def homepage():
    st.title("Home Page")

    if st.session_state.logged_in:
        st.write(f"Hello, **{st.session_state.username}**! You are logged in as **{st.session_state.role}**.")
        st.write("Use the sidebar to navigate to your dashboard.")
    else:
        st.write("This is the public homepage. Please log in to access your dashboard.")

# Main function with expanded routing
def main():
    db = connect_to_mongo()  # Connect to the database

    header()  # Show header with logout button if logged in
    toolbar()  # Show navigation options based on role

    # Enhanced routing
    if st.session_state.current_page == "Home":
        homepage()
    elif st.session_state.current_page == "Login":
        login()
    elif st.session_state.current_page == "Register":
        register_user()
    elif st.session_state.logged_in:
        if st.session_state.role == "admin":
            if st.session_state.current_page == "Manage Questions":
                manage_questions(db)
            elif st.session_state.current_page == "Student Codes":
                manage_students(db)
            elif st.session_state.current_page == "Admin Dashboard":
                admin_dashboard(db)
        else:
            if st.session_state.current_page == "My Assignments":
                student_assignments(db)
            elif st.session_state.current_page == "Student Dashboard":
                student_dashboard(db)
            elif st.session_state.current_page == "My Data":
                student_data(db)
    else:
        st.error("Page not found or access restricted.")

if __name__ == "__main__":
    main()