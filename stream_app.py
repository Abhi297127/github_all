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


# Login functionality
def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]
            st.session_state.username = username
            st.success(f"Welcome {username}!")
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
    st.rerun()


# Homepage content
def homepage():
    st.title("Welcome to the Homepage")
    st.write("This is a centralized homepage with a toolbar for navigation.")
    st.write("Use the toolbar to log in or navigate to different sections.")
    if not st.session_state.logged_in:
        login()


# Toolbar with dynamic options
def toolbar():
    st.sidebar.title("Toolbar")
    if st.session_state.logged_in:
        st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
        if st.session_state.role == "admin":
            if st.sidebar.button("Admin Dashboard"):
                admin_page()
        elif st.session_state.role == "student":
            if st.sidebar.button("Student Dashboard"):
                student_page()
        if st.sidebar.button("Logout"):
            logout()
    else:
        if st.sidebar.button("Login"):
            login()


# Main application logic
def main():
    toolbar()
    if st.session_state.logged_in:
        if st.session_state.role == "admin":
            admin_page()
        elif st.session_state.role == "student":
            student_page()
    else:
        homepage()


# Run the application
if __name__ == "__main__":
    main()
