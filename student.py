import streamlit as st
import pandas as pd

def student_dashboard(db):
    """Student Dashboard with personalized data."""
    st.subheader("Student Dashboard")
    st.write(f"Welcome, {st.session_state.role}")
    
    try:
        # Fetch recent assignments
        questions_collection = db.questions
        questions = list(questions_collection.find())
        
        if questions:
            st.write("Recent Assignments:")
            for question in questions:
                st.write(f"- **{question['question_name']}** (Class: {question['class_name']})")
        else:
            st.info("No assignments available.")
    except Exception as e:
        st.error(f"Error fetching assignments: {e}")

def student_assignments(db,username):
    """Display student's assignments with filtering options."""
    st.subheader("My Assignments")
    st.write(username)
    
    try:
        # Fetch and display questions
        questions_collection = db.questions
        questions = list(questions_collection.find({}, {"question_name": 1, "class_name": 1, "_id": 0}))

        # Connect to JavaFileAnalysis database
        java_db = db.client['JavaFileAnalysis']

        user = java_db.users.find_one({"username": username})
        if user:
            name = user.get('name')
            allowed_collections = java_db.list_collection_names()
            
            if name and name in allowed_collections:
                student_collection = java_db[name]
            else:
                raise ValueError(f"Collection '{name}' not found or user has no associated collection")
        else:
            raise ValueError(f"User with username '{username}' not found")


        # Fetch documents from JavaFileAnalysis
        documents = list(student_collection.find({}, {"added_java_files": 1, "_id": 0}))

        # Collect and sort Java keys
        added_java_keys = []
        for doc in documents:
            added_files = doc.get("added_java_files", {})
            if isinstance(added_files, dict):
                added_java_keys.extend(added_files.keys())

        # Remove duplicates and sort the keys
        added_java_keys_list = sorted(set(added_java_keys))

        # Dropdown for filtering by status
        filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])

        if questions:
            for question in questions:
                # Remove ".java" extension from class_name
                class_name = question.get('class_name', '').replace('.java', '')
                is_completed = class_name in added_java_keys_list

                # Filter based on dropdown selection
                if (filter_status == "Completed" and not is_completed) or (filter_status == "Pending" and is_completed):
                    continue

                # Display question with tick or cross symbol
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    tick_symbol = "\u2705" if is_completed else "\u274C"
                    st.write(f"{tick_symbol} {question.get('question_name', 'Unnamed Question')} - {class_name}")
        else:
            st.info("No assignments found.")
    except Exception as e:
        st.error(f"Error fetching assignments: {e}")

def student_data(db):
    """Display student's profile and submitted assignments."""
    st.subheader("My Profile and Data")
    
    try:
        # Fetch student's own data
        student_collection = db.users
        student = student_collection.find_one({"username": st.session_state.username})
        
        if student:
            st.write(f"**Name:** {student.get('full_name', 'N/A')}")
            st.write(f"**Username:** {student.get('username', 'N/A')}")
            st.write(f"**Class:** {student.get('class_name', 'N/A')}")
            
            # Fetch and display assignment submissions
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
    except Exception as e:
        st.error(f"Error fetching student data: {e}")
