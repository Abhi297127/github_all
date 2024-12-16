import streamlit as st

def admin_dashboard(db):
    st.subheader("Admin Dashboard")
    st.write("Send, Edit, or Delete questions for all students:")

    questions_collection = db.questions  # Collection name

    # Add new question
    with st.form(key="send_question_form"):
        question_name = st.text_input("Question Name")
        class_name = st.text_input("Class Name")
        submit_button = st.form_submit_button("Send Question")

        if submit_button:
            new_question = {
                "question_name": question_name,
                "class_name": class_name,
            }
            questions_collection.insert_one(new_question)  # Insert into MongoDB
            st.success("Question sent successfully!")

    # List existing questions
    st.write("Sent Questions:")
    questions = list(questions_collection.find())

    for question in questions:
        st.write(f"**{question['question_name']}** ({question['class_name']})")
        col1, col2, col3 = st.columns([1, 1, 1])

        # Edit button
        with col1:
            if st.button(f"Edit {question['question_name']}", key=f"edit_{question['_id']}"):
                edit_question(db, question)

        # Delete button
        with col2:
            if st.button(f"Delete {question['question_name']}", key=f"delete_{question['_id']}"):
                questions_collection.delete_one({"_id": question["_id"]})
                st.success("Question deleted!")
                st.rerun()

def edit_question(db, question):
    st.write("Edit Question:")
    questions_collection = db.questions
    new_question_name = st.text_input("Edit Question Name", value=question['question_name'])
    new_class_name = st.text_input("Edit Class Name", value=question['class_name'])

    if st.button("Update Question", key=f"update_{question['_id']}"):
        questions_collection.update_one(
            {"_id": question["_id"]},
            {"$set": {"question_name": new_question_name, "class_name": new_class_name}}
        )
        st.success("Question updated successfully!")
        st.rerun()