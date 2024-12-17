import streamlit as st
from bson.objectid import ObjectId
from pymongo import MongoClient

def admin_dashboard(db):
    st.subheader("Admin Overview")
    st.write("Welcome to the Admin Dashboard")
    num=db.questions.count_documents({})
    username = "abhishelke297127"
    password = "Abhi%402971"
    connection_string = f"mongodb+srv://{username}:{password}@cluster0.uu8yq.mongodb.net/?retryWrites=true&w=majority"
    
    # Connect to MongoDB
    client = MongoClient(connection_string)
    db = client["JavaFileAnalysis"]  # Replace with your actual database name

    # Get the list of collections
    collections = db.list_collection_names()

    # Count the total number of collections
    total_collections = len(collections)

    # You can add admin summary statistics here
    total_students = total_collections
    total_questions = num
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Total Questions", total_questions)

def manage_questions(db):
    st.subheader("Manage Questions")
    st.subheader("Assign Questions with Classname")
    st.write("Manage questions for all students:")

    questions_collection = db.questions

    # Initialize session state variables for new question form
    if 'new_question_name' not in st.session_state:
        st.session_state['new_question_name'] = ''
    if 'new_class_name' not in st.session_state:
        st.session_state['new_class_name'] = ''

    # Form to add new questions
    with st.form(key="send_question_form"):
        st.text_input("Question Name", key="new_question_name")  # Relying on session state
        st.text_input("Class Name", key="new_class_name")
        submit_button = st.form_submit_button("Send Question")

        if submit_button:
            question_name = st.session_state['new_question_name']
            class_name = st.session_state['new_class_name']

            if question_name and class_name:
                # Check for duplicate questions
                existing_question = questions_collection.find_one({
                    "class_name": class_name
                })

                if existing_question:
                    st.warning(f"The class '{class_name}' already has a question assigned.")
                else:
                    # Insert new question if no duplicates are found
                    new_question = {"question_name": question_name, "class_name": class_name}
                    try:
                        questions_collection.insert_one(new_question)
                        st.success("Question sent successfully!")
                        # Reset session state after submission
                        st.session_state['new_question_name'] = ""
                        st.session_state['new_class_name'] = ""
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error while sending the question: {e}")
            else:
                st.warning("Please fill in both fields to send the question.")

    # Display existing questions
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


def edit_question(db, question):
    """
    Function to edit an existing question.
    """
    questions_collection = db.questions

    st.write("### Edit Question")
    with st.form(key=f"edit_form_{question['_id']}"):
        new_question_name = st.text_input("Edit Question Name", value=question['question_name'])
        new_class_name = st.text_input("Edit Class Name", value=question['class_name'])
        save_button = st.form_submit_button("Save Changes")

        if save_button:
            try:
                updated_data = {"$set": {"question_name": new_question_name, "class_name": new_class_name}}
                questions_collection.update_one({"_id": ObjectId(question["_id"])}, updated_data)
                st.success("Question updated successfully!")
                st.session_state[f"editing_{question['_id']}"] = False  # Exit edit mode
                st.rerun()
            except Exception as e:
                st.error(f"Error while updating the question: {e}")


def delete_question(db, question_id):
    """
    Function to delete a question by ID.
    """
    questions_collection = db.questions
    try:
        result = questions_collection.delete_one({"_id": ObjectId(question_id)})
        if result.deleted_count > 0:
            st.success("Question deleted successfully!")
            st.rerun()
        else:
            st.warning("No question found to delete.")
    except Exception as e:
        st.error(f"Error while deleting the question: {e}")


def manage_students(db):
    st.subheader("Manage Students")
    
    # MongoDB credentials
    username = "abhishelke297127"
    password = "Abhi%402971"
    connection_string = f"mongodb+srv://{username}:{password}@cluster0.uu8yq.mongodb.net/?retryWrites=true&w=majority"
    
    # Connect to MongoDB
    client = MongoClient(connection_string)
    db = client["JavaFileAnalysis"]  # Replace with your actual database name

    # Get the list of collections
    collections = db.list_collection_names()
    st.write(f"Total Collections: {len(collections)}")
    if collections:
        for collection_name in collections:
            # Show the collection name in the first column
            st.write(f"{collection_name}")
    else:
        st.write("No collections found in this database.")
    


