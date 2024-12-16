import streamlit as st
from bson.objectid import ObjectId

# Admin Dashboard function
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
def admin_dashboard(db):
    st.subheader("Assign Questions with Classname")
    st.write("Manage questions for all students:")

    questions_collection = db.questions

    # Add new question form
    if 'new_question_name' not in st.session_state:
        st.session_state['new_question_name'] = ''
    if 'new_class_name' not in st.session_state:
        st.session_state['new_class_name'] = ''

    with st.form(key="send_question_form"):
        # Use session state to store form inputs, but don't overwrite them
        question_name = st.text_input("Question Name", key="new_question_name", value=st.session_state['new_question_name'])
        class_name = st.text_input("Class Name", key="new_class_name", value=st.session_state['new_class_name'])
        submit_button = st.form_submit_button("Send Question")

        if submit_button:
            if question_name and class_name:
                # Check if the combination of question_name and class_name already exists
                existing_question = questions_collection.find_one({
                    "class_name": class_name
                })

                if existing_question:
                    # Show a warning if a duplicate class_name exists
                    st.warning(f"The class '{class_name}' already has a question assigned.")
                else:
                    # Insert new question if no duplicates are found
                    new_question = {"question_name": question_name, "class_name": class_name}
                    try:
                        questions_collection.insert_one(new_question)
                        st.success("Question sent successfully!")
                        # Reset session state after successful submission
                        st.session_state['new_question_name'] = ""  # Clear the question name field
                        st.session_state['new_class_name'] = ""  # Clear the class name field
                        st.rerun()  # Refresh the page to show updated data
                    except Exception as e:
                        st.error(f"Error while sending the question: {e}")
            else:
                st.warning("Please fill in both fields to send the question.")

    # List existing questions in a table format
    st.write("### Sent Questions:")
    questions = list(questions_collection.find())

    if questions:
        for question in questions:
            col1, col2, col3 = st.columns([7, 1, 1])  # Adjust column widths
            with col1:
                st.markdown(
                    f"**{question['question_name']}** <br> *Class Name: {question['class_name']}*",
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("✏️", key=f"edit_button_{question['_id']}"):  # Edit Icon
                    st.session_state[f"editing_{question['_id']}"] = True
            with col3:
                if st.button("🗑️", key=f"delete_button_{question['_id']}"):  # Delete Icon
                    try:
                        result = questions_collection.delete_one({"_id": ObjectId(question["_id"])})
                        if result.deleted_count > 0:
                            st.success("Question deleted successfully!")
                            st.rerun()
                        else:
                            st.warning("No question found to delete.")
                    except Exception as e:
                        st.error(f"Error while deleting the question: {e}")

            # Show edit form if in edit mode
            if st.session_state.get(f"editing_{question['_id']}", False):
                edit_question(db, question)
    else:
        st.info("No questions available.")

# Edit question function
def edit_question(db, question):
    questions_collection = db.questions

    # Display the current question data in an editable form
    with st.form(key=f"edit_question_form_{question['_id']}"):
        # Pre-fill form fields with current data
        new_question_name = st.text_input(
            "Edit Question Name",
            value=question.get("question_name", ""),
            key=f"edit_name_{question['_id']}"
        )
        new_class_name = st.text_input(
            "Edit Class Name",
            value=question.get("class_name", ""),
            key=f"edit_class_{question['_id']}"
        )

        # Submit button for saving changes
        save_button = st.form_submit_button("Save Changes")

        if save_button:
            if new_question_name and new_class_name:
                try:
                    # Update question in MongoDB
                    result = questions_collection.update_one(
                        {"_id": ObjectId(question["_id"])},
                        {"$set": {"question_name": new_question_name, "class_name": new_class_name}}
                    )

                    if result.modified_count > 0:
                        st.success("Question updated successfully!")
                        st.session_state[f"editing_{question['_id']}"] = False  # Reset edit state
                        st.rerun()  # Refresh to show changes
                    else:
                        st.warning("No changes were made.")
                except Exception as e:
                    st.error(f"Error while updating the question: {e}")
            else:
                st.warning("Both fields are required to update the question.")

        # Cancel button to exit edit mode
        if st.form_submit_button("Cancel"):
            st.session_state[f"editing_{question['_id']}"] = False
