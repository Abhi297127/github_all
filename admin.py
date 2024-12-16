import streamlit as st
from bson.objectid import ObjectId

# Admin Dashboard function to handle sending, editing, and deleting questions
def admin_dashboard(db):
    st.subheader("Admin Dashboard")
    st.write("Send, Edit, or Delete questions for all students:")

    questions_collection = db.questions

    # Add new question form
    with st.form(key="send_question_form"):
        question_name = st.text_input("Question Name", key="new_question_name")
        class_name = st.text_input("Class Name", key="new_class_name")
        submit_button = st.form_submit_button("Send Question")

        if submit_button:
            if question_name and class_name:
                new_question = {"question_name": question_name, "class_name": class_name}
                try:
                    questions_collection.insert_one(new_question)
                    st.success("Question sent successfully!")
                    st.rerun()  # Refresh the page to show updated data
                except Exception as e:
                    st.error(f"Error while sending the question: {e}")
            else:
                st.warning("Please fill in both fields to send the question.")

    # List existing questions
    st.write("Sent Questions:")
    questions = list(questions_collection.find())

    if questions:
        for question in questions:
            st.write(f"**{question['question_name']}** ({question['class_name']})")
            col1 = st.columns([1, 1])
            # Delete button for each question
            with col1[0]:
                if st.button(f"Delete {question['question_name']}", key=f"delete_button_{question['_id']}"):
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

# Delete question function to handle the deletion process in the form
def delete_question(db, question):
    questions_collection = db.questions

    # Display the current question data in the form
    with st.form(key=f"delete_question_form_{question['_id']}"):
        # Show the current question name and class name in text fields (read-only)
        st.text_input("Question Name", value=question.get("question_name", ""), key=f"delete_name_{question['_id']}", disabled=True)
        st.text_input("Class Name", value=question.get("class_name", ""), key=f"delete_class_{question['_id']}", disabled=True)

        # Submit button for deleting the question
        submit_button = st.form_submit_button("Delete Question")

        if submit_button:
            try:
                # Convert `_id` to ObjectId if needed
                question_id = ObjectId(question["_id"]) if isinstance(question["_id"], str) else question["_id"]

                # Debugging: Display the ID to be deleted
                st.write("Deleting Question with ID:", question_id)

                # Delete the question from the MongoDB database
                result = questions_collection.delete_one({"_id": question_id})

                # Debugging: Display the result of the delete operation
                st.write("Delete Result:", result.raw_result)

                if result.deleted_count > 0:
                    st.success("Question deleted successfully!")
                    st.rerun()  # Refresh the page to show updated data
                else:
                    st.warning("No question found to delete.")
            except Exception as e:
                # Debugging: Display the exception for troubleshooting
                st.error(f"An error occurred while deleting: {e}")
