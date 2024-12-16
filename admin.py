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
    st.write("Edit Question:")
    questions_collection = db.questions

    # Get current question details
    new_question_name = st.text_input("Edit Question Name", value=question['question_name'])
    new_class_name = st.text_input("Edit Class Name", value=question['class_name'])

    if st.button("Update Question", key=f"update_{question['_id']}"):
        try:
            # Ensure _id is handled as an ObjectId
            questions_collection.update_one(
                {"_id": ObjectId(question["_id"])},
                {"$set": {"question_name": new_question_name, "class_name": new_class_name}}
            )
            st.success("Question updated successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"An error occurred: {e}")
