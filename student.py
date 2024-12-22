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

def student_assignments(db):
    st.subheader("My Assignments")
    
    # Fetch and display questions
    questions_collection = db.questions
    questions = list(questions_collection.find())

    # Connect to JavaFileAnalysis database
    java_db = db.client['JavaFileAnalysis']
    student_collection = java_db['Abhishek_Shelke']
    student_files = list(student_collection.find())

    # Extract class names from student files
    class_names_in_files = {file.get('class_name', '').join('.java') for file in student_files}

    # Dropdown for filtering by status
    filter_status = st.selectbox("Filter by Status", ["All", "Pending", "Completed"])

    if questions:
        for question in questions:
            class_name = question.get('class_name', '').split('.')[0]
            is_completed = class_name in class_names_in_files

            # Filter logic based on dropdown selection
            if (filter_status == "Completed" and not is_completed) or (filter_status == "Pending" and is_completed):
                continue

            # Display question with tick symbol if completed
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