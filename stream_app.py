import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import os
from pymongo import MongoClient

# MongoDB connection
def get_mongo_client():
    client = MongoClient("mongodb://localhost:27017/")  # Adjust your connection string as needed
    return client

# Fetch data for the fixed database and collection
def fetch_data(collection_name):
    client = get_mongo_client()
    db = client["JavaFileAnalysis"]  # Fixed database name
    collection = db[collection_name]
    data = list(collection.find())  # Convert cursor to list
    return data

# Process data into a DataFrame
def process_data(data):
    rows = []
    seen_commit_ids = set()  # Track already added commit IDs

    total_counts = {
        "Total Added Files": 0,
        "Total Renamed Files": 0,
        "Total Modified Files": 0,
        "Total Deleted Files": 0,
    }

    for doc in data:
        commit_id = doc.get("commit_id", "N/A")
        if commit_id in seen_commit_ids:
            continue
        seen_commit_ids.add(commit_id)

        # Extract filenames and counts for each category
        added_files = extract_files(doc.get("added_java_files", {}))
        renamed_files = extract_files(doc.get("renamed_java_files", {}))
        modified_files = extract_files(doc.get("modified_java_files", {}))
        deleted_files = extract_files(doc.get("deleted_java_files", {}))

        # Update total counts
        total_counts["Total Added Files"] += len(added_files)
        total_counts["Total Renamed Files"] += len(renamed_files)
        total_counts["Total Modified Files"] += len(modified_files)
        total_counts["Total Deleted Files"] += len(deleted_files)

        row = {
            "Commit ID": commit_id,
            "Commit Date": doc.get("commit_date", "N/A"),
            "Commit Time": doc.get("commit_time", "N/A"),
            "Commit Message": doc.get("commit_message", "N/A"),
            "Added Files Count": len(added_files),
            "Added File Names": ", ".join(added_files) if added_files else "0",
            "Renamed Files Count": len(renamed_files),
            "Renamed File Names": ", ".join(renamed_files) if renamed_files else "0",
            "Modified Files Count": len(modified_files),
            "Modified File Names": ", ".join(modified_files) if modified_files else "0",
            "Deleted Files Count": len(deleted_files),
            "Deleted File Names": ", ".join(deleted_files) if deleted_files else "0",
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    return df, total_counts

# Extract filenames from nested dictionaries
def extract_files(files_dict):
    filenames = []
    for key, value in files_dict.items():
        filenames.extend(value)
    return filenames

# Generate visualizations
def generate_charts(df):
    st.subheader("Visualizations")

    # Total Files Actioned
    action_totals = df[["Added Files Count", "Renamed Files Count", "Modified Files Count", "Deleted Files Count"]].sum()
    action_totals = pd.DataFrame(action_totals, columns=["Total Files"]).reset_index()
    action_totals.rename(columns={"index": "Action Type"}, inplace=True)

    fig = px.pie(action_totals, values="Total Files", names="Action Type", title="Distribution of File Actions")
    st.plotly_chart(fig)

    # Bar Chart of Files Added/Modified Per Commit
    fig2 = px.bar(
        df,
        x="Commit ID",
        y=["Added Files Count", "Renamed Files Count", "Modified Files Count", "Deleted Files Count"],
        title="File Actions Per Commit",
        labels={"value": "File Count", "variable": "Action Type"},
        barmode="group",
    )
    st.plotly_chart(fig2)

# Export to PDF
def export_to_pdf(df, total_counts):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Java File Analysis Report", ln=True, align="C")
    pdf.ln(10)

    # Total Counts
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Summary of File Actions:", ln=True)
    pdf.ln(5)
    for action, count in total_counts.items():
        pdf.cell(200, 10, txt=f"{action}: {count}", ln=True)
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", style="B", size=12)
    col_width = pdf.w / (len(df.columns) + 1)  # Adjust column width dynamically
    for col in df.columns:
        pdf.cell(col_width, 10, col[:30], border=1, align="C")  # Truncate column names for layout
    pdf.ln()

    # Table Data
    pdf.set_font("Arial", size=10)
    for index, row in df.iterrows():
        for col in df.columns:
            pdf.cell(col_width, 10, str(row[col])[:30], border=1)  # Truncate data for layout
        pdf.ln()

    # Save PDF to buffer
    buffer = BytesIO()
    buffer.write(pdf.output(dest="S").encode("latin1"))
    buffer.seek(0)
    return buffer

# Streamlit App
def main():
    st.title("Java File Analysis - Enhanced Viewer")

    import pymongo

    connection_string = "mongodb://abhishelke297127:Abhi%402971@cluster0-shard-00-00.uu8yq.mongodb.net:27017,cluster0-shard-00-01.uu8yq.mongodb.net:27017,cluster0-shard-00-02.uu8yq.mongodb.net:27017/test?ssl=true&replicaSet=atlas-12345-shard-0&authSource=admin&retryWrites=true&w=majority"

    client = pymongo.MongoClient(connection_string, tls=True, tlsAllowInvalidCertificates=False)
    db = client["JavaFileAnalysis"]
    collection_names = db.list_collection_names()

    # Let the user choose a collection
    collection_name = st.selectbox("Select Collection", collection_names)

    if collection_name:
        raw_data = fetch_data(collection_name)

        if raw_data:
            processed_data, total_counts = process_data(raw_data)

            # Display the total counts
            st.subheader("Summary of File Actions")
            for action, count in total_counts.items():
                st.write(f"**{action}:** {count}")

            # Display the data table
            st.subheader("Commit Data")
            st.dataframe(processed_data, use_container_width=True)

            # Add visualizations
            generate_charts(processed_data)

            # Option to download the data as CSV
            st.download_button(
                "Download Data as CSV",
                processed_data.to_csv(index=False),
                file_name="commit_data.csv",
                mime="text/csv",
            )

            # Option to download the data as PDF
            pdf_buffer = export_to_pdf(processed_data, total_counts)
            st.download_button(
                "Download Report as PDF",
                pdf_buffer,
                file_name="commit_report.pdf",
                mime="application/pdf",
            )

        else:
            st.warning("No data available in this collection.")

    # Refresh button
    if st.button("Refresh Data"):
        st.rerun()

if __name__ == "__main__":
    main()
