import streamlit as st
from bson.objectid import ObjectId

def admin_dashboard(db):
    st.subheader("Admin Dashboard")
    st.write("Send, Edit, or Delete questions for all students:")

    questions_collection = db.questions

    # Add new question
    with st.form(key="send_question_form"):
        question_name = st.text_input("Question Name", key="new_question_name")
        class_name = st.text_input("Class Name", key="new_class_name")
        submit_button = st.form_submit_button("Send Question")

        if submit_button:
            new_question = {"question_name": question_name, "class_name": class_name}
            questions_collection.insert_one(new_question)
            st.success("Question sent successfully!")
            st.rerun()

    # List existing questions
    st.write("Sent Questions:")
    questions = list(questions_collection.find())

    for question in questions:
        st.write(f"**{question['question_name']}** ({question['class_name']})")
        col1, col2 = st.columns([1, 1])

        # Edit
        with col1:
            if st.button(f"Edit {question['question_name']}", key=f"edit_button_{question['_id']}"):
                edit_question(db, question)

        # Delete
        with col2:
            if st.button(f"Delete {question['question_name']}", key=f"delete_button_{question['_id']}"):
                questions_collection.delete_one({"_id": ObjectId(question["_id"])})
                st.success("Question deleted successfully!")
                st.rerun()

def edit_question(db, question):
    questions_collection = db.questions

    # Display the current question data in the form
    with st.form(key=f"edit_question_form_{question['_id']}"):
        # Capture user input for fields
        new_question_name = st.text_input(
            "Edit Question Name", value=question["question_name"], key=f"edit_name_{question['_id']}"
        )
        new_class_name = st.text_input(
            "Edit Class Name", value=question["class_name"], key=f"edit_class_{question['_id']}"
        )
        submit_button = st.form_submit_button("Update Question")

        if submit_button:
            # Build the `update_fields` dynamically based on changed values
            update_fields = {}

            if new_question_name != question["question_name"]:
                update_fields["question_name"] = new_question_name
            if new_class_name != question["class_name"]:
                update_fields["class_name"] = new_class_name

            # Apply updates only if there are changes
            if update_fields:
                try:
                    question_id = ObjectId(question["_id"]) if isinstance(question["_id"], str) else question["_id"]

                    # Update the question in the MongoDB database
                    result = questions_collection.update_one(
                        {"_id": question_id},  # Match the question by its unique ID
                        {"$set": update_fields}  # Dynamically update only changed fields
                    )
                    if result.modified_count > 0:
                        st.success("Question updated successfully!")
                    else:
                        st.warning("No changes made to the question.")
                    st.rerun()  # Refresh the page to show updated data
                except Exception as e:
                    st.error(f"An error occurred while updating: {e}")
            else:
                st.info("No changes detected.")
