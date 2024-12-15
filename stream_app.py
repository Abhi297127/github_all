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

# Custom CSS for styling
def add_custom_css():
    st.markdown(
        """
        <style>
        /* Add gradient background */
        body {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: #fff;
            font-family: Arial, sans-serif;
        }
        /* Style the title */
        .title {
            text-align: center;
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 20px;
            color: #ffffff;
            text-shadow: 2px 2px 4px #000000;
        }
        /* Center the login form */
        .form-container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 30px;
            width: 400px;
            margin: 50px auto;
            box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.3);
        }
        input, button {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: none;
            border-radius: 5px;
        }
        input {
            background: #ffffff;
            color: #000;
        }
        button {
            background: #ff6a00;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #e05500;
        }
        .logout-btn {
            background: #d9534f;
            color: white;
            font-weight: bold;
        }
        .logout-btn:hover {
            background: #c9302c;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def login():
    st.markdown('<h1 class="title">Login Page</h1>', unsafe_allow_html=True)

    # Login form
    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

def admin_page():
    st.markdown('<h1 class="title">Admin Dashboard</h1>', unsafe_allow_html=True)
    st.write("Welcome to the admin dashboard!")
    if st.button("Logout", key="admin_logout", help="Log out from admin", use_container_width=True):
        logout()

def student_page():
    st.markdown('<h1 class="title">Student Dashboard</h1>', unsafe_allow_html=True)
    st.write(f"Welcome, {st.session_state.username}!")
    if st.button("Logout", key="student_logout"):
        logout()

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.rerun()

# Add custom CSS
add_custom_css()

# Main logic
if st.session_state.logged_in:
    if st.session_state.role == "admin":
        admin_page()
    elif st.session_state.role == "student":
        student_page()
else:
    login()
