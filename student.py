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
            i=1
            for question in questions:
                st.write(f" ** {i}. {question['question_name']}** (Class: {question['class_name']})")
                i+=1
        else:
            st.info("No assignments available.")
    except Exception as e:
        st.error(f"Error fetching assignments: {e}")

def student_assignments(db, username):
    """Display student's assignments with filtering options."""
    st.subheader("My Assignments")
    st.write(username)
    
    try:
        # Fetch and display questions
        questions_collection = db.questions
        questions = list(questions_collection.find({}, {"question_name": 1, "class_name": 1, "_id": 0}))

        if not isinstance(questions, list):
            raise ValueError("Questions fetch returned a non-list object.")

        # Connect to LoginData database to find user
        login_db = db.client['LoginData']
        
        # Search for the user across all collections in LoginData
        name = None
        for collection_name in login_db.list_collection_names():
            user = login_db[collection_name].find_one({"username": username})
            if user:
                name = user['name']
                break
        
        if not name:
            raise ValueError(f"User with username '{username}' not found in any collection")

        # Switch to JavaFileAnalysis database
        java_analysis_db = db.client['JavaFileAnalysis']

        # Search for student's collection in JavaFileAnalysis
        added_java_keys = []
        documents = []
        
        if name in java_analysis_db.list_collection_names():
            student_collection = java_analysis_db[name]
            documents = list(student_collection.find({}, {"added_java_files": 1, "_id": 0}))
            
            if not isinstance(documents, list):
                raise ValueError("Document fetch returned a non-list object.")
            
            for doc in documents:
                added_files = doc.get("added_java_files", {})
                if isinstance(added_files, dict):
                    added_java_keys.extend(added_files.keys())
        else:
            st.warning(f"No collection found for '{name}' in JavaFileAnalysis.")

        # Remove duplicates and sort the keys
        added_java_keys_list = sorted(set(added_java_keys))

        # Count completed and pending assignments
        completed_count = 0
        pending_count = 0

        for question in questions:
            class_name = question.get('class_name', '').replace('.java', '')
            if class_name in added_java_keys_list:
                completed_count += 1
            else:
                pending_count += 1

        # Dropdown for filtering by status with counts
        filter_status = st.selectbox(
            "Filter by Status",
            [f"All ({len(questions)})", 
             f"Pending ({pending_count})", 
             f"Completed ({completed_count})"]
        )

        # Display filtered assignments
        if questions:
            for question in questions:
                class_name = question.get('class_name', '').replace('.java', '')
                is_completed = class_name in added_java_keys_list

                # Filter based on dropdown selection
                if ("Pending" in filter_status and is_completed) or ("Completed" in filter_status and not is_completed):
                    continue

                # Display question with tick or cross symbol
                col1, col2 = st.columns([0.9, 0.1])
                with col1:
                    tick_symbol = "\u2705" if is_completed else "\u274C"
                    st.write(f"{tick_symbol} {question.get('question_name', 'Unnamed Question')} - {class_name}")
        else:
            st.info("No assignments found.")
    
    except ValueError as ve:
        st.error(f"Value Error: {ve}")
    
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
