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
@st.cache_data(ttl=600)
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
    st.sidebar.title("\U0001F4CA Navigation")
    return st.sidebar.radio(
        "Go to", 
        ["Home", "All Data", "Visualization Charts", "Codes"],
        index=0
    )

# Refresh Button
def refresh_data():
    st.cache_data.clear()
    st.experimental_rerun()

# Main app
def main():
    st.title("\U0001F680 Java File Analysis")
    st.caption("Analyze and visualize Java file actions efficiently.")

    # Sidebar navigation
    page = sidebar()

    # Add Refresh Button
    if st.sidebar.button("\u21bb Refresh Data"):
        refresh_data()

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
        st.image("java.jpg", caption="Java File Analysis Dashboard", use_column_width=True)

    elif page == "All Data":
        st.subheader("All Data")

        # Collection selection
        collection_name = st.selectbox("\U0001F4C2 Select Collection", collection_names)
        raw_data = fetch_data(collection_name) if collection_name else []

        # Date filtering
        start_date = st.date_input("\U0001F4C5 Start Date", value=datetime(2023, 1, 1))
        end_date = st.date_input("\U0001F4C5 End Date", value=datetime(2024, 1, 1))

        if raw_data:
            processed_data, total_counts = process_data(raw_data)

            # Filter by date range
            processed_data["Commit Date"] = pd.to_datetime(processed_data["Commit Date"], errors='coerce')
            filtered_data = processed_data[
                (processed_data["Commit Date"] >= pd.to_datetime(start_date)) &
                (processed_data["Commit Date"] <= pd.to_datetime(end_date))
            ]

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
        collection_name = st.selectbox("\U0001F4C2 Select Collection", collection_names)
        raw_data = fetch_data(collection_name) if collection_name else []

        if raw_data:
            processed_data, total_counts = process_data(raw_data)
            action_type = st.selectbox(
                "\U0001F4CA Select Action Type",
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
