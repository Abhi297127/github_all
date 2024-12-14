import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from datetime import datetime

# MongoDB connection
def get_mongo_client():
    try:
        client = MongoClient(
            "mongodb+srv://abhishelke297127:Abhi%402971@cluster0.uu8yq.mongodb.net/?retryWrites=true&w=majority",
            tls=True,
            tlsAllowInvalidCertificates=False
        )
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {e}")
        return None

# Fetch data for the fixed database and collection
def fetch_data(collection_name):
    client = get_mongo_client()
    if client is None:
        return []

    db = client["JavaFileAnalysis"]
    collection = db[collection_name]
    return list(collection.find())

# Process data into a DataFrame
def process_data(data):
    rows = []
    total_counts = {
        "Total Added Files": 0,
        "Total Renamed Files": 0,
        "Total Modified Files": 0,
        "Total Deleted Files": 0,
    }

    for doc in data:
        added_files = doc.get("added_java_files", {}).values()
        renamed_files = doc.get("renamed_java_files", {}).values()
        modified_files = doc.get("modified_java_files", {}).values()
        deleted_files = doc.get("deleted_java_files", {}).values()

        row = {
            "Commit ID": doc.get("commit_id", "N/A"),
            "Commit Date": doc.get("commit_date", "N/A"),
            "Added Files": ", ".join(sum(added_files, [])),
            "Renamed Files": ", ".join(sum(renamed_files, [])),
            "Modified Files": ", ".join(sum(modified_files, [])),
            "Deleted Files": ", ".join(sum(deleted_files, [])),
        }

        # Update counts
        total_counts["Total Added Files"] += len(sum(added_files, []))
        total_counts["Total Renamed Files"] += len(sum(renamed_files, []))
        total_counts["Total Modified Files"] += len(sum(modified_files, []))
        total_counts["Total Deleted Files"] += len(sum(deleted_files, []))

        rows.append(row)

    df = pd.DataFrame(rows)
    return df, total_counts

# Sidebar navigation
def sidebar():
    st.sidebar.title("📊 Navigation")
    return st.sidebar.radio(
        "Go to", 
        ["Home", "All Data", "Visualization Charts"],
        index=0,
        help="Navigate between different sections of the app."
    )

# Add custom CSS
def add_custom_css():
    st.markdown(
        """
        <style>
        /* Background color */
        .css-1d391kg {background-color: #f5f5f5;}
        
        /* Header and subheader styles */
        .stTitle {color: #1f4e79; font-size: 2.2rem; font-weight: bold;}
        .stSubheader {color: #34568b; font-weight: bold;}
        
        /* Sidebar styles */
        .css-1aumxhk {background-color: #234e70;}
        .css-1aumxhk h1 {color: white;}
        .css-1aumxhk label, .css-1aumxhk .stRadio > div {color: #c0d6df;}
        
        /* Buttons and download links */
        .stDownloadButton {background-color: #ff914d; color: white; border: none; padding: 8px 15px; border-radius: 5px;}
        .stDownloadButton:hover {background-color: #ff6f3c;}
        .css-1aehpvq {color: #ff6f3c;}
        
        /* Dataframe table */
        .dataframe {font-size: 0.9rem;}
        </style>
        """,
        unsafe_allow_html=True
    )

# Main app
def main():
    # Add custom CSS
    add_custom_css()

    st.title("🚀 Java File Analysis")
    st.caption("Analyze and visualize Java file actions efficiently.")
    
    # Sidebar navigation
    page = sidebar()

    # MongoDB connection
    client = get_mongo_client()
    if not client:
        return

    db = client["JavaFileAnalysis"]
    collection_names = db.list_collection_names()

    if page == "Home":
        st.subheader("Welcome to Java File Analysis!")
        st.write(
            """
            This application allows you to:
            - View all file actions from your MongoDB database.
            - Explore visualizations of added, renamed, modified, and deleted files.
            """
        )
        st.image("https://via.placeholder.com/800x400", caption="Java File Analysis Dashboard", use_container_width=True)

    elif page == "All Data":
        st.subheader("All Data")

        # Collection selection
        collection_name = st.selectbox("📂 Select Collection", collection_names)
        raw_data = fetch_data(collection_name) if collection_name else []

        # Date filtering
        start_date = st.date_input("📅 Start Date", value=datetime(2023, 1, 1))
        end_date = st.date_input("📅 End Date", value=datetime(2024, 1, 1))

        # Filter data
        if raw_data:
            processed_data, total_counts = process_data(raw_data)

            # Filter by date range
            if "Commit Date" in processed_data.columns:
                processed_data["Commit Date"] = pd.to_datetime(processed_data["Commit Date"])
                filtered_data = processed_data[
                    (processed_data["Commit Date"] >= pd.to_datetime(start_date)) &
                    (processed_data["Commit Date"] <= pd.to_datetime(end_date))
                ]
            else:
                filtered_data = processed_data

            # Display total counts
            st.write("### Total File Counts")
            for action, count in total_counts.items():
                st.write(f"**{action}:** {count}")

            # Display filtered data
            st.write("### Data Table")
            st.dataframe(filtered_data, use_container_width=True)

    elif page == "Visualization Charts":
        st.subheader("Visualization Charts")

        # Collection selection
        collection_name = st.selectbox("📂 Select Collection", collection_names)
        raw_data = fetch_data(collection_name) if collection_name else []

        # Chart filters
        if raw_data:
            processed_data, total_counts = process_data(raw_data)
            action_type = st.selectbox(
                "📊 Select Action Type",
                ["Added Files", "Renamed Files", "Modified Files", "Deleted Files"]
            )

            # Generate charts
            if action_type in processed_data.columns:
                chart_data = processed_data[["Commit Date", action_type]].copy()
                chart_data["Count"] = chart_data[action_type].apply(lambda x: len(x.split(", ")))

                fig = px.bar(
                    chart_data,
                    x="Commit Date",
                    y="Count",
                    title=f"{action_type} Over Time",
                    color_discrete_sequence=["#4caf50"]
                )
                st.plotly_chart(fig)

if __name__ == "__main__":
    main()
