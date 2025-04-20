from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import glob
from document_processor import process_documents
from rag_system import RAGSystem
from agents import QuestionAnsweringAgent, DocumentAnalysisAgent
import utils
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Find the PDF directory - try multiple approaches
def find_pdf_directory():
    # Try the expected path
    expected_path = os.path.normpath("F:/softograph/rag_langchain_project/data/pdfs")
    
    if os.path.exists(expected_path):
        logger.info(f"Found PDF directory at expected path: {expected_path}")
        return expected_path
    
    # Try relative to the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join(os.path.dirname(current_dir), 'data', 'pdfs')
    
    if os.path.exists(relative_path):
        logger.info(f"Found PDF directory at relative path: {relative_path}")
        return relative_path
    
    # Create the directory if it doesn't exist
    os.makedirs(expected_path, exist_ok=True)
    logger.info(f"Created PDF directory: {expected_path}")
    return expected_path

PDF_DIR = find_pdf_directory()
logger.info(f"Using PDF directory: {PDF_DIR}")

# Check if directory contains PDFs
pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
if pdf_files:
    logger.info(f"Found {len(pdf_files)} PDF files in {PDF_DIR}")
else:
    logger.warning(f"No PDF files found in {PDF_DIR}")

# Initialize the RAG system
rag_system = RAGSystem(pdf_dir=PDF_DIR)

# Initialize the agents
qa_agent = QuestionAnsweringAgent(rag_system)
analysis_agent = DocumentAnalysisAgent(rag_system)

@app.route('/api/health', methods=['GET'])
def health_check():
    pdf_count = len(glob.glob(os.path.join(PDF_DIR, "*.pdf")))
    return jsonify({
        "status": "healthy", 
        "pdf_directory": PDF_DIR,
        "pdf_count": pdf_count
    }), 200

@app.route('/api/process-documents', methods=['POST'])
def process_docs():
    try:
        # Process all PDFs in the configured PDF directory
        result = process_documents(PDF_DIR)
        
        # Initialize the RAG system with the processed documents
        rag_system.initialize_vector_store()
        
        return jsonify({
            "status": "success", 
            "message": f"Processed {result['processed']} documents", 
            "details": result,
            "pdf_directory": PDF_DIR
        }), 200
    except Exception as e:
        logger.exception("Error processing documents")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.json
        query = data.get('query', '')
        if not query:
            return jsonify({"status": "error", "message": "Query is required"}), 400
        
        # Use the QA agent to answer the question
        response = qa_agent.answer_question(query)
        
        return jsonify({
            "status": "success", 
            "answer": response["answer"],
            "sources": response["sources"]
        }), 200
    except Exception as e:
        logger.exception("Error answering question")
        return jsonify({"status": "error", "message": str(e)}), 500

# @app.route('/api/analyze', methods=['POST'])
# def analyze_documents():
#     try:
#         data = request.json
#         analysis_type = data.get('analysis_type', 'summary')
        
#         # Use the analysis agent to analyze the documents
#         result = analysis_agent.analyze_documents(analysis_type)
        
#         return jsonify({
#             "status": "success", 
#             "analysis": result
#         }), 200
#     except Exception as e:
#         logger.exception("Error analyzing documents")
#         return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    try:
        documents = utils.list_documents(PDF_DIR)
        
        return jsonify({
            "status": "success", 
            "documents": documents,
            "pdf_directory": PDF_DIR
        }), 200
    except Exception as e:
        logger.exception("Error getting documents")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)