import streamlit as st

def student_dashboard(db):
    st.subheader("Student Dashboard")
    st.write(f"Welcome, {st.session_state.role}!")

    # Refresh button
    if st.button("Refresh Data", key="refresh_button"):
        st.rerun()  # Refresh the page to fetch the latest data

    # Fetch questions from MongoDB
    questions_collection = db.questions
    questions = list(questions_collection.find())

    if questions:
        st.write("Your Questions:")
        num = 1
        for question in questions:
            st.write(f"{num}. **{question['question_name']}** (Class: {question['class_name']})")
            num += 1
    else:
        st.info("No questions available.")
def student_data(db):
    st.subheader("Student Data")
