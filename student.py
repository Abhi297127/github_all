import streamlit as st

def student_dashboard(db):
    st.subheader("Student Dashboard")
    st.write(f"Welcome, {st.session_state.username}!")

    # Fetch questions from MongoDB
    questions_collection = db.questions
    questions = list(questions_collection.find())

    if questions:
        st.write("Your Questions:")
        for question in questions:
            st.write(f"**{question['question_name']}** ({question['class_name']})")
    else:
        st.write("No questions available.")
