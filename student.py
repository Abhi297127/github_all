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
    
    if questions:
        for question in questions:
            with st.expander(f"{question['question_name']} - {question['class_name']}"):
                st.write("Assignment Details:")
                st.write(f"**Class Name :** {question['class_name']}")
                
                # Optional: File upload for submission
                uploaded_file = st.file_uploader(
                    f"Submit assignment for {question['question_name']}", 
                    key=f"file_{question['_id']}"
                )
                
                if uploaded_file is not None:
                    # Process file upload logic
                    st.success(f"File {uploaded_file.name} uploaded successfully!")
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