import streamlit as st
from bson.objectid import ObjectId

# Admin Dashboard function to handle sending, editing, and deleting questions
def admin_dashboard(db):
    st.subheader("Assign Questions with Class Name")
    st.write("Send, Edit, or Delete questions for all students:")

    questions_collection = db.questions

    # Initialize session state variables to store input values
    if 'question_name' not in st.session_state:
        st.session_state['question_name'] = ""
    if 'class_name' not in st.session_state:
        st.session_state['class_name'] = ""

    # Add new question form
    with st.form(key="send_question_form"):
        question_name = st.text_input("Question Name", key="new_question_name", value=st.session_state['question_name'])
        class_name = st.text_input("Class Name", key="new_class_name", value=st.session_state['class_name'])
        submit_button = st.form_submit_button("Send Question")

        if submit_button:
            if question_name and class_name:
                new_question = {"question_name": question_name, "class_name": class_name}
                try:
                    questions_collection.insert_one(new_question)
                    st.session_state['question_name'] = ""  # Reset the question name
                    st.session_state['class_name'] = ""  # Reset the class name
                    st.success("Question sent successfully!")
                except Exception as e:
                    st.error(f"Error while sending the question: {e}")
            else:
                st.warning("Please fill in both fields to send the question.")
            st.rerun()  # Refresh the page to show updated data

    # List existing questions
    st.write("### Sent Questions:")
    questions = list(questions_collection.find())

    if questions:
        for question in questions:
            st.write(f"**{question['question_name']}** (Class: {question['class_name']})")

            # Display Edit and Delete buttons in columns
            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("Edit", key=f"edit_button_{question['_id']}"):
                    edit_question(db, question)  # Call edit functionality

            with col2:
                if st.button("Delete", key=f"delete_button_{question['_id']}"):
                    try:
                        result = questions_collection.delete_one({"_id": ObjectId(question["_id"])})
                        if result.deleted_count > 0:
                            st.success("Question deleted successfully!")
                            st.rerun()  # Refresh the page to show updated data
                        else:
                            st.warning("No question found to delete.")
                    except Exception as e:
                        st.error(f"Error while deleting the question: {e}")
    else:
        st.info("No questions available.")

# Function to edit a question
def edit_question(db, question):
    questions_collection = db.questions

    # Display the current question data in an editable form
    with st.form(key=f"edit_question_form_{question['_id']}"):
        new_question_name = st.text_input("Edit Question Name", value=question.get("question_name", ""), key=f"edit_name_{question['_id']}")
        new_class_name = st.text_input("Edit Class Name", value=question.get("class_name", ""), key=f"edit_class_{question['_id']}")

        # Submit button for saving changes
        save_button = st.form_submit_button("Save Changes")

        if save_button:
            if new_question_name and new_class_name:
                try:
                    result = questions_collection.update_one(
                        {"_id": ObjectId(question["_id"])},
                        {"$set": {"question_name": new_question_name, "class_name": new_class_name}}
                    )
                    if result.modified_count > 0:
                        st.success("Question updated successfully!")
                        st.rerun()  # Refresh the page to show updated data
                    else:
                        st.warning("No changes were made.")
                except Exception as e:
                    st.error(f"Error while updating the question: {e}")
            else:
                st.warning("Both fields are required to update the question.")
