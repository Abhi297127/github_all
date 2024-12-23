import streamlit as st
import pandas as pd

def student_dashboard(db):
    st.subheader("Student Dashboard")
    st.write(f"Welcome, {st.session_state.role}")
    
    # Fetch recent assignments
    questions_collection = db.questions
    questions = list(questions_collection.find())
    
    if questions:
        st.write("Recent Assignments:")
        for question in questions:
            st.write(f"- **{question['question_name']}** (Class: {question['class_name']})")
    else:
        st.info("No assignments available.")
        """Student dashboard with personalized data."""

def student_assignments(db):
    st.subheader("My Assignments")
    # st.write(f"Hello, {st.session_state['name']}!")
    # student_name=st.session_state['name']
    # Fetch and display questions
    questions_collection = db.questions
    questions = list(questions_collection.find({}, {"question_name": 1, "class_name": 1, "_id": 0}))

    # Extract only the class_name field from questions
    class_names_list = [question.get('class_name', '') for question in questions]

    # Output the class names
    # st.write("Class Names in Questions:", class_names_list)

        # Connect to JavaFileAnalysis database
    java_db = db.client['JavaFileAnalysis']

    student_collection = java_db['Pooja_Yadav']  # Replace with the correct student collection

    # Fetch all documents and extract keys from the `added_java_files` field
    documents = list(student_collection.find({}, {"added_java_files": 1, "_id": 0}))

    # Collect all keys from `added_java_files` across documents
    added_java_keys = []  # Using a list to store the keys
    for doc in documents:
        added_files = doc.get("added_java_files", {})
        if isinstance(added_files, dict):
            added_java_keys.extend(added_files.keys())  # Add keys to the list

    # Remove duplicates (if necessary) and sort the keys
    added_java_keys_list = sorted(set(added_java_keys))

    # Display the keys
    # st.write("Class Names from `added_java_files`:", added_java_keys_list)

    # Dropdown for filtering by status
    filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])

    if questions:
        for question in questions:
            # Remove the ".java" extension from the class_name in questions
            class_name = question.get('class_name', '').replace('.java', '')
            is_completed = class_name in added_java_keys_list

            # Filter logic based on dropdown selection
            if (filter_status == "Completed" and not is_completed) or (filter_status == "Pending" and is_completed):
                continue

            # Display question with tick or cross symbol if completed
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                tick_symbol = "\u2705" if is_completed else "\u274C"
                st.write(f"{tick_symbol} {question.get('question_name', 'Unnamed Question')} - {class_name}")
    else:
        st.info("No assignments found.")



def student_data(db):
    st.subheader("My Profile and Data")
    
    # Fetch student's own data
    student_collection = db.users
    student = student_collection.find_one({"username": st.session_state.username})
    
    if student:
        st.write(f"**Name:** {student.get('full_name', 'N/A')}")
        st.write(f"**Username:** {student.get('username', 'N/A')}")
        st.write(f"**Class:** {student.get('class_name', 'N/A')}")
        
        # Optional: Fetch and display assignment submissions if you have a submissions collection
        submissions_collection = db.submissions
        submissions = list(submissions_collection.find({"username": st.session_state.username}))
        
        if submissions:
            st.write("### Submitted Assignments")
            for submission in submissions:
                st.write(f"- {submission.get('assignment_name', 'Unknown Assignment')}")
                st.write(f"  Submitted on: {submission.get('submission_date', 'N/A')}")
        else:
            st.info("No assignment submissions found.")
    else:
        st.error("Student data not found.")