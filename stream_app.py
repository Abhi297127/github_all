import streamlit as st

# Mock credentials for demonstration
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "student1": {"password": "student123", "role": "student"},
    "student2": {"password": "student456", "role": "student"},
}

# Mock database for storing questions
questions_db = {}

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
    
    # Admin can send questions to students
    st.write("Send a question to a student:")

    # Form for sending question
    with st.form(key="send_question_form"):
        student_username = st.selectbox("Select Student", ["student1", "student2"])
        question_name = st.text_input("Question Name")
        class_name = st.text_input("Class Name")
        submit_button = st.form_submit_button("Send Question")

        if submit_button:
            # Store the question in the mock database
            if student_username not in questions_db:
                questions_db[student_username] = []
            questions_db[student_username].append({"question_name": question_name, "class_name": class_name})
            st.success(f"Question sent to {student_username}!")

    # Display the list of all questions sent to the students
    if questions_db:
        st.write("Sent Questions:")
        for student, questions in questions_db.items():
            st.write(f"Questions for {student}:")
            for q in questions:
                st.write(f"- {q['question_name']} ({q['class_name']})")


# Student dashboard
def student_page():
    st.subheader("Student Dashboard")
    st.write(f"Welcome, {st.session_state.username}!")
    
    # Display questions sent to the logged-in student
    if st.session_state.username in questions_db:
        st.write("Your Questions:")
        for q in questions_db[st.session_state.username]:
            st.write(f"- {q['question_name']} ({q['class_name']})")
    else:
        st.write("No questions have been sent to you yet.")


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

    # Define navigation options based on login status
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


# Header with top-right Logout button
def header():
    cols = st.columns([5, 1])  # Adjust column width ratio
    with cols[0]:
        st.write("")  # Placeholder for alignment
    with cols[1]:
        if st.session_state.logged_in:
            if st.button("Logout", key="logout_button"):
                logout()


# Main application logic
def main():
    header()
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
