import streamlit as st
from pymongo import MongoClient
from admin import admin_dashboard
from student import student_dashboard
import os

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

# User credentials (dummy data)
USERS = {
    "AF0454940": {"password": "Adi123", "role": "Aditi_Sandbhor"},
    "AF0454887": {"password": "Bhu123", "role": "Bhushan_Ingle"},
    "AF0454880": {"password": "Ath123", "role": "Atharv_Patekar"},
    "AF0447939": {"password": "Shu123", "role": "Shubhangi_Pawar"},
    "AF0447938": {"password": "Poo123", "role": "Pooja_Yadav"},
    "AF0446979": {"password": "Ama123", "role": "Aman_Bisen"},
    "AF0446974": {"password": "Bin123", "role": "Bindiya_Shetty"},
    "AF0446959": {"password": "Rut123", "role": "Rutik_Danavale"},
    "AF0443189": {"password": "San123", "role": "Sanket_Chivhe"},
    "AF0442897": {"password": "Abh123", "role": "Abhishek_Shelke"},
    "AF0442752": {"password": "Vai123", "role": "Vaishnavi_Deshmukh"},
    "AF0441275": {"password": "Lub123", "role": "Lubna_Kazi"},
    "AF0441263": {"password": "Sak123", "role": "Sakshi_Khopade"},
    "AF0441258": {"password": "Pra123", "role": "Prachi_Salunkhe"},
    "AF0441204": {"password": "San123", "role": "Sanket_Bhoite"},
    "AF0441190": {"password": "Adi123", "role": "Aditi_Zanje"},
    "AF0441188": {"password": "Vai123", "role": "Vaishnavi_Mane"},
    "AF0441187": {"password": "Dip123", "role": "Dipak_Kondhalkar"},
    "AF0441186": {"password": "Omk123", "role": "Omkar_Kudale"},
    "AF0441185": {"password": "Man123", "role": "Mangesh_Kolapkar"},
    "AF0441184": {"password": "Nik123", "role": "Nikita_Karape"},
    "AF0441183": {"password": "Pra123", "role": "Prabhat_Sharma"},
    "AF0441182": {"password": "Dha123", "role": "Dhananjay_Ghate"},
    "AF0441128": {"password": "Bhu123", "role": "Bhuvan_Bhoge"},
    "AF0441090": {"password": "Shu123", "role": "Shubham_Chavan"},
    "AF0441088": {"password": "Omk123", "role": "Omkar_Gaikwad"},
    "AF0436726": {"password": "Ani123", "role": "Aniruddha_Sanjay_Vinchurkar"},
    "AF0436715": {"password": "Yas123", "role": "Yash_Mankar"},
    "AF0434724": {"password": "San123", "role": "Sanskruti_Kale"},
    "AF0434723": {"password": "Sur123", "role": "Suraj_Yadav"},
    "AF0434722": {"password": "Pra123", "role": "Pranav_Tamboi"},
    "AF0434721": {"password": "Shr123", "role": "Shruti_Chaudhari"},
    "AF0434720": {"password": "Shr123", "role": "Shreyash_Pawar"},
    "AF0434656": {"password": "Aac123", "role": "Aachal_Akre"},
    "AF0434651": {"password": "Pra123", "role": "Pravin_Subrav_Gunjal"},
    "AF0434647": {"password": "Kai123", "role": "Kaivalya_Kulkarni"},
    "AF0434643": {"password": "Bhu123", "role": "Bhushan_Sonje"},
    "AF0417977": {"password": "Vis123", "role": "Vishruti_Rane"},
    "AF0417313": {"password": "Shri123", "role": "Shriya_Wankhede"},
    "AF0417095": {"password": "Vai123", "role": "Vaibhav_Bhange"},
    "AF0413014": {"password": "Aar123", "role": "Aarya_Shinde"},
    "AF0412826": {"password": "Sid123", "role": "Siddhant_Mane"},
    "AF0412380": {"password": "Ank123", "role": "Ankush_Mishra"},
    "AF0315573": {"password": "Mad123", "role": "Madhuri_Shinde"}
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

# Main function
def main():
    db = connect_to_mongo()  # Connect to the database

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
