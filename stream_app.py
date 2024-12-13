import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from io import BytesIO
from fpdf import FPDF
import os
import datetime

# Enhanced Custom CSS for Modern UI
def local_css():
    st.markdown("""
    <style>
    /* Global Styles */
    :root {
        --primary-color: #4a6cf7;
        --secondary-color: #6c757d;
        --background-color: #f4f7fa;
        --card-background: #ffffff;
        --text-color: #333333;
    }

    /* Smooth Background Gradient */
    .stApp {
        background: linear-gradient(135deg, var(--background-color) 0%, #e9ecef 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Elegant Card Design */
    .card {
        background: var(--card-background);
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12);
    }

    /* Button Styles */
    .stButton>button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #3a5af3 !important;
        transform: scale(1.05);
    }

    /* Metrics Styling */
    .metric-container {
        background-color: var(--card-background);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.08);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: var(--primary-color);
    }

    .metric-label {
        color: var(--secondary-color);
        font-size: 0.9rem;
        margin-top: 5px;
    }

    /* DataTable Styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Sidebar Enhancements */
    .css-1aumxhk {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    </style>
    """, unsafe_allow_html=True)

# MongoDB Connection with Enhanced Error Handling
def get_mongo_client():
    try:
        # Replace with your secure connection method
        connection_string = "mongodb+srv://abhishelke297127:Abhi%402971@cluster0.uu8yq.mongodb.net/?retryWrites=true&w=majority"
        
        client = MongoClient(connection_string, 
                             tls=True, 
                             tlsAllowInvalidCertificates=False,
                             serverSelectionTimeoutMS=5000)
        
        # Verify connection
        client.admin.command('ping')
        st.toast('MongoDB Connection Successful! 🌟', icon='✅')
        return client
    except Exception as e:
        st.error(f"❌ MongoDB Connection Error: {e}")
        st.warning("Please check your connection string and network.")
        return None

# Data Processing Functions
def fetch_data(collection_name):
    client = get_mongo_client()
    if client is None:
        return []
    
    db = client["JavaFileAnalysis"]
    collection = db[collection_name]
    
    data = list(collection.find())
    return data

def process_data(data):
    if not data:
        st.warning("No data to process.")
        return pd.DataFrame(), {}
    
    rows = []
    seen_commit_ids = set()

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
            "Added Files": len(added_files),
            "Renamed Files": len(renamed_files),
            "Modified Files": len(modified_files),
            "Deleted Files": len(deleted_files)
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    return df, total_counts

def extract_files(files_dict):
    filenames = []
    for key, value in files_dict.items():
        filenames.extend(value)
    return filenames

# Advanced Visualizations
def generate_advanced_charts(df):
    st.markdown("## 📊 Detailed Visualizations")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie Chart for File Actions
        fig1 = px.pie(
            values=df[['Added Files', 'Renamed Files', 'Modified Files', 'Deleted Files']].sum(),
            names=['Added', 'Renamed', 'Modified', 'Deleted'],
            title='File Action Distribution',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Bar Chart for Commit Statistics
        fig2 = go.Figure(data=[
            go.Bar(name='Added Files', x=df['Commit ID'], y=df['Added Files'], marker_color='#58D68D'),
            go.Bar(name='Renamed Files', x=df['Commit ID'], y=df['Renamed Files'], marker_color='#5DADE2'),
            go.Bar(name='Modified Files', x=df['Commit ID'], y=df['Modified Files'], marker_color='#F39C12'),
            go.Bar(name='Deleted Files', x=df['Commit ID'], y=df['Deleted Files'], marker_color='#EC7063')
        ])
        fig2.update_layout(
            title='File Actions per Commit',
            xaxis_title='Commit ID',
            yaxis_title='Number of Files',
            barmode='group'
        )
        st.plotly_chart(fig2, use_container_width=True)

# PDF Export Function (Simplified)
def export_to_pdf(df, total_counts):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, "Java File Analysis Report", ln=True, align="C")
    pdf.ln(10)

    # Total Counts
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, "Summary of File Actions:", ln=True)
    for action, count in total_counts.items():
        pdf.cell(0, 10, f"{action}: {count}", ln=True)
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", style="B", size=10)
    headers = list(df.columns)
    col_width = pdf.w / (len(headers) + 1)
    for header in headers:
        pdf.cell(col_width, 10, header, border=1)
    pdf.ln()

    # Table Data
    pdf.set_font("Arial", size=8)
    for _, row in df.iterrows():
        for col in headers:
            pdf.cell(col_width, 10, str(row[col]), border=1)
        pdf.ln()

    # Save to BytesIO
    buffer = BytesIO()
    buffer.write(pdf.output(dest="S").encode("latin1"))
    buffer.seek(0)
    return buffer

# Main Streamlit App
def main():
    # Apply Custom CSS
    local_css()
    
    # Set Page Configuration
    st.set_page_config(
        page_title="Java File Analysis Dashboard",
        page_icon="🖥️",
        layout="wide"
    )
    
    # Application Title with Cool Effect
    st.markdown("""
    <h1 style='text-align: center; color: #4a6cf7; 
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    background: linear-gradient(to right, #4a6cf7, #826bf7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;'>
    🖥️ Java File Analysis Dashboard
    </h1>
    """, unsafe_allow_html=True)
    
    # Connection and Data Retrieval
    client = get_mongo_client()
    if client is None:
        return

    db = client["JavaFileAnalysis"]
    collection_names = db.list_collection_names()

    # Sidebar for Collection Selection
    st.sidebar.title("🔍 Analysis Configuration")
    collection_name = st.sidebar.selectbox("Select Collection", collection_names)

    # Data Processing
    if collection_name:
        raw_data = fetch_data(collection_name)

        if raw_data:
            processed_data, total_counts = process_data(raw_data)

            # Metrics Display
            st.markdown("## 📊 Summary Metrics")
            metrics_cols = st.columns(4)
            metrics = [
                ("Total Added Files", total_counts["Total Added Files"]),
                ("Total Renamed Files", total_counts["Total Renamed Files"]),
                ("Total Modified Files", total_counts["Total Modified Files"]),
                ("Total Deleted Files", total_counts["Total Deleted Files"])
            ]

            for i, (label, value) in enumerate(metrics):
                with metrics_cols[i]:
                    st.markdown(f"""
                    <div class='metric-container'>
                        <div class='metric-value'>{value}</div>
                        <div class='metric-label'>{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Detailed DataTable
            st.markdown("## 📝 Detailed Commit Analysis")
            st.dataframe(processed_data, use_container_width=True)

            # Advanced Visualizations
            generate_advanced_charts(processed_data)

            # Download Options
            st.markdown("## 📤 Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📄 Download CSV",
                    data=processed_data.to_csv(index=False),
                    file_name=f"java_file_analysis_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="csv-download"
                )
            
            with col2:
                st.download_button(
                    label="📋 Download PDF Report",
                    data=export_to_pdf(processed_data, total_counts),
                    file_name=f"java_file_analysis_report_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key="pdf-download"
                )

        else:
            st.warning("No data available in this collection.")

if __name__ == "__main__":
    main()
    
    