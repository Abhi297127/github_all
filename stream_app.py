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

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"


# Login functionality
def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

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


# Admin dashboard
def admin_page():
    st.subheader("Admin Dashboard")
    st.write("Welcome to the admin dashboard!")
    st.write("You can add admin-specific functionality here.")


# Student dashboard
def student_page():
    st.subheader("Student Dashboard")
    st.write(f"Welcome, {st.session_state.username}!")
    st.write("You can add student-specific functionality here.")


# Logout functionality
def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.current_page = "Home"
    st.rerun()


# Homepage content
def homepage():
    st.title("Welcome to the Homepage")
    st.write("This is the Home page of the application.")
    st.write("Navigate to other sections using the sidebar.")


# Toolbar with dynamic options
def toolbar():
    st.sidebar.title("Navigation")
    options = ["Home", "Login"]
    if st.session_state.logged_in:
        options += ["Admin Dashboard" if st.session_state.role == "admin" else "Student Dashboard", "Logout"]
    selected_option = st.sidebar.radio("Go to:", options, key="sidebar_navigation")

    if selected_option == "Home":
        st.session_state.current_page = "Home"
    elif selected_option == "Login":
        st.session_state.current_page = "Login"
    elif selected_option == "Admin Dashboard" and st.session_state.logged_in:
        st.session_state.current_page = "Admin Dashboard"
    elif selected_option == "Student Dashboard" and st.session_state.logged_in:
        st.session_state.current_page = "Student Dashboard"
    elif selected_option == "Logout":
        logout()


# Main application logic
def main():
    toolbar()

    if st.session_state.current_page == "Home":
        homepage()
    elif st.session_state.current_page == "Login":
        login()
    elif st.session_state.current_page == "Admin Dashboard" and st.session_state.logged_in:
        admin_page()
    elif st.session_state.current_page == "Student Dashboard" and st.session_state.logged_in:
        student_page()


# Run the application
if __name__ == "__main__":
    main()
