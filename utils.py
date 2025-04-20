import os
import json
import hashlib
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_documents(pdf_directory):
    """
    List all PDF documents in the given directory with metadata.
    """
    if not os.path.exists(pdf_directory):
        logger.error(f"PDF directory does not exist: {pdf_directory}")
        return []
    
    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
    
    result = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        try:
            # Get file stats
            stats = os.stat(pdf_path)
            size_kb = stats.st_size / 1024
            modified_date = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            # Generate a hash for the file (first 1MB only for performance)
            file_hash = generate_file_hash(pdf_path)
            
            result.append({
                "filename": pdf_file,
                "size_kb": round(size_kb, 2),
                "modified_date": modified_date,
                "hash": file_hash
            })
        except Exception as e:
            logger.error(f"Error processing file metadata for {pdf_file}: {str(e)}")
            result.append({
                "filename": pdf_file,
                "error": str(e)
            })
    
    return result

def generate_file_hash(file_path, read_bytes=1024*1024):
    """
    Generate a hash for a file (reading only the first portion for efficiency).
    """
    h = hashlib.sha256()
    with open(file_path, 'rb') as file:
        chunk = file.read(read_bytes)
        h.update(chunk)
    return h.hexdigest()

def sanitize_filename(filename):
    """
    Sanitize a filename to ensure it's safe for file system operations.
    """
    # Replace potentially dangerous characters
    safe_filename = ''.join(c for c in filename if c.isalnum() or c in '._- ')
    return safe_filename

def save_json_data(data, filepath):
    """
    Save JSON data to a file.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON data: {str(e)}")
        return False

def load_json_data(filepath):
    """
    Load JSON data from a file.
    """
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON data: {str(e)}")
        return None