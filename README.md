# LangChain RAG Document System

A PDF document processing and question-answering system built with Flask, LangChain, and Google's Gemini models, featuring a Streamlit UI.

## Features

- Upload and process PDF documents
- Ask questions about document content
- Browse document library
- User-friendly Streamlit interface

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with your Google API key: `GOOGLE_API_KEY=your_key_here`
4. Start Flask backend: `python app.py`
5. Start Streamlit frontend: `streamlit run streamlit_app.py`
6. Access the UI at http://localhost:8501

## Configuration

- Document chunking:  using the **RecursiveCharacterTextSplitter** with a default chunk size of 1000 characters and an overlap of 200 characters
- To modify chunk size, edit parameters in `rag_system.py`

## Architecture

- Flask backend API (document processing, vector storage)
- RAG System (LangChain + Gemini)
- Streamlit frontend (user interface)
