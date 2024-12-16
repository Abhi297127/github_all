import streamlit as st
from bson.objectid import ObjectId

def admin_dashboard(db):
    st.subheader("Admin Overview")
    st.write("Welcome to the Admin Dashboard")
    
    # You can add admin summary statistics here
    total_students = db.users.count_documents({})
    total_questions = db.questions.count_documents({})
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Total Questions", total_questions)

def manage_questions(db):
    st.subheader("Manage Questions")
    questions_collection = db.questions

    # Existing question management code remains the same as in the previous admin_dashboard
    # (Keep the existing form for adding, editing, and deleting questions)

def manage_students(db):
    st.subheader("Manage Students")
    
    # Add student functionality
    st.write("Add New Student")
    with st.form(key="add_student_form"):
        username = st.text_input("Username")
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        class_name = st.text_input("Class")
        
        submit_button = st.form_submit_button("Add Student")
        
        if submit_button:
            if username and full_name and email and class_name:
                new_student = {
                    "username": username,
                    "full_name": full_name,
                    "email": email,
                    "class_name": class_name
                }
                try:
                    db.users.insert_one(new_student)
                    st.success(f"Student {full_name} added successfully!")
                except Exception as e:
                    st.error(f"Error adding student: {e}")
            else:
                st.warning("Please fill in all fields")

    # List existing students
    st.write("### Existing Students")
    students = list(db.users.find())
    
    if students:
        for student in students:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{student.get('full_name', 'N/A')}**")
                st.write(f"Username: {student.get('username', 'N/A')}")
                st.write(f"Class: {student.get('class_name', 'N/A')}")
            with col2:
                if st.button("🗑️", key=f"delete_{student['_id']}"):
                    try:
                        db.users.delete_one({"_id": student['_id']})
                        st.success("Student deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting student: {e}")
    else:
        st.info("No students found.")