import streamlit as st
from pymongo import MongoClient
from urllib.parse import urlparse
from admin import admin_dashboard, manage_students, manage_questions
from student import student_dashboard, student_assignments, student_data
from github import BadCredentialsException, Github, UnknownObjectException
import requests
from datetime import datetime
import os
import re

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

def login():
    """Log in an existing user."""
    client = MongoClient(connection_string)
    login_db = client["LoginData"]
    st.title("Login")

    # User inputs for login
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Initialize session state for button and login status
    if "login_clicked" not in st.session_state:
        st.session_state["login_clicked"] = False
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # Conditionally display login button
    if not st.session_state["login_clicked"]:
        login_button = st.button("Login")  # Display login button

        if login_button:
            st.session_state["login_clicked"] = True  # Mark button as clicked

    # If the login button is clicked, start the login process and show the loader
    if st.session_state["login_clicked"]:
        with st.spinner("Logging in and fetching data..."):
            # Verify user credentials
            user = login_db.users.find_one({"username": username, "password": password})
            
            if user:

                # Store session details
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Welcome {user['name']}!")
                # Extract owner and repository from GitHub link
                github_link = user['github_link']
                github_token = user['github_token']
                name = user['name']
                owner, repo = extract_owner_repo(github_link)
                GITHUB_TOKEN = str(github_token)
                HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

                if user["role"] == "admin":
                    st.session_state["current_page"] = "Admin Dashboard"
                else:
                    if check_repo_visibility(owner, repo, HEADERS):  # Pass HEADERS here
                        db = client.github_data
                        fetch_commits_and_files(owner, repo, db, HEADERS, name)  # Pass HEADERS here
                        st.success("Data Fetch successfully")
                    st.session_state["current_page"] = "Student Dashboard"
                st.session_state["login_clicked"] = False  # Reset the login button state
                st.rerun()  # Rerun the app to apply changes
            else:
                st.error("Invalid Username or Password")
                st.session_state["login_clicked"] = False  # Reset the button state if login fails

# Assuming 'connection_string' and MongoDB client setup are already defined

def extract_owner_repo(github_url):
    """Extract owner and repository name from GitHub URL."""
    github_url = github_url.rstrip(".git")
    parsed_url = urlparse(github_url)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]
    return None, None

# Function to validate username format

# Function to check if GitHub repo is public
def is_github_repo_public(github_token, owner, repo):
    """Check if the GitHub repository is public and token has access."""
    try:
        g = Github(github_token)
        repository = g.get_repo(f"{owner}/{repo}")
        
        # Check if the repository is public
        if repository.private:
            st.error("GitHub repository is private.")
            return False

        # Check if the user has access to the repository
        # If the user has no access, an UnknownObjectException will be raised
        repository.get_contents("")
        return True
    except UnknownObjectException:
        st.error("Token does not have access to this repository.")
        return False
    except Exception as e:
        st.error("Error accessing GitHub repository. Ensure the repository exists and the token is correct.")
        return False

# Username validation pattern
def validate_username(username):
    pattern = r"^AF0[3-4][0-7]\d{4}$"  # Matches AF0300000 to AF0470000
    return bool(re.match(pattern, username))

def register_user():
    """Register a new user."""
    st.title("Register")
    
    # MongoDB connection
    client = MongoClient(connection_string)
    login_db = client["LoginData"]

    # Input fields
    name = st.text_input("Name", placeholder="Enter your full name")
    username = st.text_input("Username", placeholder="Enter username (e.g., AF0300000)")
    github_link = st.text_input("GitHub Repository Link", placeholder="Enter your GitHub repository link")
    github_token = st.text_input("GitHub Token", type="password", placeholder="Enter your GitHub token")
    
    # Validation flags
    valid_name = bool(name.strip())
    valid_username = validate_username(username)
    valid_github = False
    valid_token = bool(github_token)
    password = None

    # Validate GitHub link
    if github_link and github_token:
        owner, repo = extract_owner_repo(github_link)
        if owner and repo and is_github_repo_public(github_token, owner, repo):
            st.success("GitHub Repository is Public")
            valid_github = True
            password = st.text_input("Set Password", type="password", placeholder="Enter your password")
        else:
            st.error("GitHub repository is private or inaccessible.")

    # Error handling (single error message per field)
    errors = []
    if not valid_name:
        errors.append("Name cannot be empty.")
    if not valid_username:
        errors.append("Invalid username format. Use format like AF0300000.")
    if not github_link:
        errors.append("GitHub link is required.")
    if not valid_token:
        errors.append("GitHub token is required.")

    # Show errors collectively
    if errors:
        st.error("\n".join(errors))

    # Show Submit button if all fields are valid
    if valid_name and valid_username and valid_github and valid_token and password:
        if st.button("Submit"):
            existing_user = login_db["users"].find_one({"username": username})
            existing_repo = login_db["users"].find_one({"github_link": github_link})
            if existing_user and existing_repo:
                st.error("Both username and GitHub link already exist.")
            elif existing_user:
                st.error("Username already exists.")
            elif existing_repo:
                st.error("GitHub link already exists.")
            else:
                login_db["users"].insert_one({
                    "name": name,
                    "username": username,
                    "github_link": github_link,
                    "password": password,
                    "github_token": github_token,
                    "role": "student"
                })
                st.success("Data added successfully")
    else:
        st.info("Please complete all fields and ensure the repository is valid to enable submission.")


def check_repo_visibility(owner, repo, headers):
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(repo_url, headers=headers)  # Use passed headers here
    if response.status_code == 200:
        repo_data = response.json()
        if repo_data.get("private"):
            st.warning("The repository is private.")
            return False
        else:
            # st.info("The repository is public.")
            return True
    else:
        st.error(f"Error: Unable to fetch repository details (Status Code: {response.status_code})")
        return False

def fetch_commits_and_files(owner, repo, db, headers,username):
    commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    page = 1
    collection_name = username

    if collection_name in db.list_collection_names():
        db[collection_name].drop()
        # st.info(f"Dropped existing collection: {collection_name}")

    while True:
        response = requests.get(f"{commits_url}?page={page}&per_page=100", headers=headers)  # Use passed headers here
        if response.status_code == 200:
            commits = response.json()
            if not commits:
                break

            for commit in commits:
                sha = commit["sha"]
                commit_date = commit["commit"]["committer"]["date"]

                commit_datetime = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
                formatted_date = commit_datetime.strftime("%Y-%m-%d")
                formatted_time = commit_datetime.strftime("%H:%M:%S")
                commit_message = commit["commit"]["message"]

                commit_detail_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
                commit_detail_response = requests.get(commit_detail_url, headers=headers)  # Use passed headers here
                if commit_detail_response.status_code == 200:
                    commit_data = commit_detail_response.json()
                    files = commit_data.get("files", [])

                    added_java_files = {}
                    modified_java_files = {}
                    renamed_java_files = {}
                    deleted_java_files = {}

                    for file in files:
                        if file["filename"].endswith(".java"):
                            status = file["status"]
                            filename = os.path.splitext(os.path.basename(file["filename"]))[0]

                            if status == "renamed":
                                previous_filename = os.path.splitext(os.path.basename(file.get("previous_filename", "")))[0]
                                renamed_java_files[previous_filename] = filename
                                raw_url = file.get("raw_url")
                                if raw_url:
                                    file_response = requests.get(raw_url, headers=headers)  # Use passed headers here
                                    if file_response.status_code == 200:
                                        modified_java_files[filename] = file_response.text

                            elif status in ["added", "modified"]:
                                raw_url = file.get("raw_url")
                                if raw_url:
                                    file_response = requests.get(raw_url, headers=headers)  # Use passed headers here
                                    if file_response.status_code == 200:
                                        file_content = file_response.text
                                if status == "added":
                                    added_java_files[filename] = file_content
                                elif status == "modified":
                                    modified_java_files[filename] = file_content

                            elif status == "removed":
                                deleted_java_files[filename] = ""

                    commit_doc = {
                        "commit_id": sha,
                        "commit_date": formatted_date,
                        "commit_time": formatted_time,
                        "commit_message": commit_message,
                        "added_java_files": added_java_files,
                        "modified_java_files": modified_java_files,
                        "renamed_java_files": renamed_java_files,
                        "deleted_java_files": deleted_java_files
                    }
                    db[collection_name].insert_one(commit_doc)
            page += 1
        else:
            st.error(f"Error fetching commits: {response.status_code}")
            break

    # st.info("Data has been inserted into MongoDB.")

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