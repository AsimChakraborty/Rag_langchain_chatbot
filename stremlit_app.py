import streamlit as st
import requests
import json
import os
import pandas as pd
from datetime import datetime
import io

# Set page configuration
st.set_page_config(
    page_title="Document RAG System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API URL
API_URL = "http://localhost:5000/api"

# Function to make API calls
def api_call(endpoint, method="GET", data=None):
    url = f"{API_URL}/{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            st.error(f"Unsupported method: {method}")
            return None
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"API Connection Error: {str(e)}")
        return None

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #EFF6FF;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #1F2937; /* Dark gray text for contrast */
    }
    .source-box {
        background-color: #F3F4F6;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        color: #1F2937; /* Dark gray text for contrast */
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📚 LangChain RAG Document System</div>', unsafe_allow_html=True)

# Get system health to check connection
health_result = api_call("health")
if health_result and health_result.get("status") == "healthy":
    pdf_directory = health_result.get("pdf_directory", "Unknown")
    pdf_count = health_result.get("pdf_count", 0)
else:
    pdf_directory = "Unknown"
    pdf_count = 0

# Sidebar
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio("Select a page", ["Home", "Document Explorer", "Question Answering", "Upload PDFs"])
    
    st.markdown("### Actions")
    if st.button("Process Documents"):
        with st.spinner("Processing documents..."):
            result = api_call("process-documents", method="POST")
            if result and result.get("status") == "success":
                st.success(f"Successfully processed {result['message']}")
                st.json(result.get("details", {}))
            else:
                st.error("Failed to process documents")
    
    st.markdown("### System Info")
    st.info(f"""
    PDF Directory: {pdf_directory}
    PDFs Found: {pdf_count}
    
    API Status: {"✅ Online" if health_result else "❌ Offline"}
    """)

# Home page
if page == "Home":
    st.markdown('<div class="sub-header">Welcome to the Document RAG System</div>', unsafe_allow_html=True)
    
    st.markdown("""
    This system allows you to:
    
    1. Process multiple PDF documents
    2. Ask questions about the document content
    3. Analyze document themes and key points
    4. Explore document metadata
    
    **Getting Started:**
    - Navigate to the **Upload PDFs** page to add new documents
    - Navigate to the **Document Explorer** to see available documents
    - Use the **Process Documents** button in the sidebar to index your documents
    - Go to **Question Answering** to query your documents
    - Explore insights with **Document Analysis**
    """)
    
    # Display system health status
    if health_result and health_result.get("status") == "healthy":
        st.success("✅ System is online and ready")
    else:
        st.error("❌ System is offline or experiencing issues")

# Document Explorer page
elif page == "Document Explorer":
    st.markdown('<div class="sub-header">Document Explorer</div>', unsafe_allow_html=True)
    
    # Get document list
    with st.spinner("Loading documents..."):
        docs_result = api_call("documents")
        
    if docs_result and docs_result.get("status") == "success":
        documents = docs_result.get("documents", [])
        pdf_dir = docs_result.get("pdf_directory", "Unknown")
        
        st.info(f"PDF Directory: {pdf_dir}")
        
        if not documents:
            st.warning("No documents found. Please upload PDF files using the 'Upload PDFs' page.")
        else:
            # Convert to DataFrame for better display
            df = pd.DataFrame(documents)
            
            # Display as table
            st.dataframe(
                df,
                column_config={
                    "filename": "Document Name",
                    "size_kb": st.column_config.NumberColumn("Size (KB)", format="%.2f KB"),
                    "modified_date": "Last Modified",
                    "hash": "Document Hash"
                },
                hide_index=True
            )
            
            # Display document count
            st.info(f"Total documents: {len(documents)}")
    else:
        st.error("Failed to load document list")

# Question Answering page
elif page == "Question Answering":
    st.markdown('<div class="sub-header">Ask Questions About Your Documents</div>', unsafe_allow_html=True)
    
    # Query input
    query = st.text_input("Enter your question:", placeholder="What are the main topics covered in the documents?")
    
    if st.button("Submit Question"):
        if query:
            with st.spinner("Generating answer..."):
                result = api_call("ask", method="POST", data={"query": query})
            
            if result and result.get("status") == "success":
                # Display answer
                st.markdown("### Answer")
                st.markdown(f'<div class="info-box">{result["answer"]}</div>', unsafe_allow_html=True)
                
                # Display sources
                st.markdown("### Sources")
                for i, source in enumerate(result.get("sources", [])):
                    st.markdown(f"""
                    <div class="source-box">
                        <strong>Source {i+1}:</strong> {source.get('metadata', {}).get('source', 'Unknown')}
                        <br/>
                        <em>{source.get('content', 'No content preview available')}</em>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Failed to get response")
        else:
            st.warning("Please enter a question")

# Upload PDFs page
elif page == "Upload PDFs":
    st.markdown('<div class="sub-header">Upload PDF Documents</div>', unsafe_allow_html=True)
    
    # Get PDF directory from API
    health_result = api_call("health")
    if health_result and health_result.get("status") == "healthy":
        pdf_directory = health_result.get("pdf_directory", "Unknown")
    else:
        pdf_directory = "Unknown"
    
    st.info(f"""
    Current PDF Directory: {pdf_directory}
    
    Upload your PDFs below, then click the 'Process Documents' button in the sidebar to index them.
    """)
    
    # File uploader
    uploaded_files = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Save Uploaded Files"):
            saved_files = []
            failed_files = []
            
            for uploaded_file in uploaded_files:
                try:
                    # Create destination path
                    dest_path = os.path.join(pdf_directory, uploaded_file.name)
                    
                    # Save the file
                    with open(dest_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    saved_files.append(uploaded_file.name)
                except Exception as e:
                    failed_files.append(f"{uploaded_file.name} - Error: {str(e)}")
            
            if saved_files:
                st.success(f"Successfully saved {len(saved_files)} PDF files:")
                for file in saved_files:
                    st.write(f"- {file}")
                
                st.info("Next steps: Click 'Process Documents' in the sidebar to index the documents.")
            
            if failed_files:
                st.error(f"Failed to save {len(failed_files)} PDF files:")
                for file in failed_files:
                    st.write(f"- {file}")