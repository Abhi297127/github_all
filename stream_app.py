import streamlit as st
from pymongo import MongoClient
from urllib.parse import quote_plus
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# ---- Database Connection ----
@st.cache_resource
def get_mongo_client():
    username = "abhishelke297127"
    password = "Abhi@2971"
    encoded_username = quote_plus(username)
    encoded_password = quote_plus(password)
    uri = f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.uu8yq.mongodb.net/?retryWrites=true&w=majority"
    try:
        client = MongoClient(uri)
        client.admin.command('ping')  # Test connection
        return client
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {e}")
        return None

# Fetch Data from MongoDB
def fetch_data(collection_name="file_actions"):
    client = get_mongo_client()
    if client:
        db = client['java_file_analysis']
        collection = db[collection_name]
        data = list(collection.find())
        return data
    return []

# ---- Streamlit UI ----
def main():
    st.set_page_config(page_title="Java File Analysis Dashboard", layout="wide")
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.radio("Go to", ["Home", "All Data", "Visualization Charts"])

    if page == "Home":
        display_home()
    elif page == "All Data":
        display_all_data()
    elif page == "Visualization Charts":
        display_visualization_charts()

# ---- Page Functions ----
def display_home():
    st.title("🚀 Java File Analysis")
    st.write("### Welcome to Java File Analysis!")
    st.markdown("""
        This application allows you to:
        - View all file actions from your MongoDB database.
        - Explore visualizations of added, renamed, modified, and deleted files.
    """)
    
    # Placeholder for visual
    st.warning(
        "**Note:** Update deprecated parameters like `use_column_width` in upcoming Streamlit versions.",
        icon="⚠️"
    )
    st.image("https://via.placeholder.com/800x400.png", caption="Java File Analysis Dashboard")

def display_all_data():
    st.title("📄 All Data")
    st.write("### Table of All File Actions")

    # Fetch Data
    raw_data = fetch_data()
    if raw_data:
        df = pd.DataFrame(raw_data)
        st.write("#### Total Files in Commit:", len(df))
        
        # Clean DataFrame (remove '_id')
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])
        
        st.dataframe(df)
    else:
        st.error("No data found. Please check your database connection.")

def display_visualization_charts():
    st.title("📊 Visualization Charts")
    st.write("### Explore File Actions Visually")

    # Fetch Data
    raw_data = fetch_data()
    if raw_data:
        df = pd.DataFrame(raw_data)

        # Ensure the columns exist
        if "action" in df.columns:
            # Count of Actions
            action_counts = df['action'].value_counts()
            st.write("#### File Action Counts")
            fig = px.bar(
                x=action_counts.index,
                y=action_counts.values,
                labels={"x": "File Actions", "y": "Count"},
                title="Distribution of File Actions",
                color=action_counts.index
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Line Chart for Dates
            if "date" in df.columns:
                st.write("#### File Actions Over Time")
                df['date'] = pd.to_datetime(df['date'])  # Ensure 'date' is datetime
                date_counts = df.groupby('date').size().reset_index(name='count')
                fig_line = px.line(
                    date_counts,
                    x='date',
                    y='count',
                    title="File Actions Over Time",
                    labels={"date": "Date", "count": "Number of Actions"}
                )
                st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.warning("The 'action' column is missing from the data.")
    else:
        st.error("No data found. Please check your database connection.")

if __name__ == "__main__":
    main()
