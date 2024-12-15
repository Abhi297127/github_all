import streamlit as st

# Mock credentials for demonstration
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "student1": {"password": "student123", "role": "student"},
    "student2": {"password": "student456", "role": "student"},
}

# Persisted database to store questions (for this session, simulating with a dictionary)
if "questions_db" not in st.session_state:
    st.session_state.questions_db = []

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

    # Admin can send or edit questions for all students
    st.write("Send, Edit, or Delete a question for all students:")

    with st.form(key="send_edit_question_form"):
        question_name = st.text_input("Question Name")
        class_name = st.text_input("Class Name")
        submit_button = st.form_submit_button("Send/Update Question")

        if submit_button:
            # Add or update the question in the mock database
            question = {
                "question_name": question_name,
                "class_name": class_name
            }
            st.session_state.questions_db.append(question)
            st.success("Question sent/updated to all students!")

    # Display the list of questions with options to edit or delete
    if len(st.session_state.questions_db) > 0:
        st.write("Sent Questions:")
        for idx, question in enumerate(st.session_state.questions_db):
            st.write(f"**{question['question_name']}** ({question['class_name']})")

            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button(f"Edit {question['question_name']}", key=f"edit_{idx}"):
                    st.session_state.questions_db[idx] = {
                        "question_name": st.text_input("Edit Question Name", value=question['question_name']),
                        "class_name": st.text_input("Edit Class Name", value=question['class_name'])
                    }

            with col2:
                if st.button(f"Delete {question['question_name']}", key=f"delete_{idx}"):
                    st.session_state.questions_db.pop(idx)
                    st.rerun()

# Student dashboard
def student_page():
    st.subheader("Student Dashboard")
    st.write(f"Welcome, {st.session_state.username}!")

    # Display the question sent to all students by the admin
    if len(st.session_state.questions_db) > 0:
        st.write("Your Questions:")
        for question in st.session_state.questions_db:
            st.write(f"**{question['question_name']}** ({question['class_name']})")
    else:
        st.write("No questions have been sent yet.")

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
