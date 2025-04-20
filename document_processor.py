import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_documents(pdf_directory):
    """
    Process all PDF documents in the given directory.
    Returns a dictionary with processing results.
    """
    logger.info(f"Processing documents from directory: {pdf_directory}")
    
    # Handle Windows path issues by normalizing the path
    pdf_directory = os.path.normpath(pdf_directory)
    
    if not os.path.exists(pdf_directory):
        logger.error(f"PDF directory does not exist: {pdf_directory}")
        logger.info("Trying alternative approaches to find the directory...")
        
        # Try to find the directory relative to the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        relative_pdf_dir = os.path.join(os.path.dirname(current_dir), 'data', 'pdfs')
        
        if os.path.exists(relative_pdf_dir):
            logger.info(f"Found relative PDF directory: {relative_pdf_dir}")
            pdf_directory = relative_pdf_dir
        else:
            # If still not found, try with raw string path
            raw_path = r"F:\softograph\rag_langchain_project\data\pdfs"
            if os.path.exists(raw_path):
                logger.info(f"Found PDF directory with raw path: {raw_path}")
                pdf_directory = raw_path
            else:
                raise FileNotFoundError(f"PDF directory not found: {pdf_directory}")
    
    # Find PDF files using glob pattern (more robust across platforms)
    pdf_pattern = os.path.join(pdf_directory, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {pdf_directory}")
        logger.info("Available files in directory:")
        try:
            all_files = os.listdir(pdf_directory)
            for file in all_files:
                logger.info(f"  - {file}")
        except:
            logger.error("Could not list directory contents")
        
        return {"processed": 0, "failed": 0, "files": []}
    
    # Get just the filenames, not the full paths
    pdf_filenames = [os.path.basename(f) for f in pdf_files]
    logger.info(f"Found {len(pdf_files)} PDF files: {pdf_filenames}")
    
    # Initialize counters and results
    processed_count = 0
    failed_count = 0
    processed_files = []
    
    # Create text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    # Process each PDF
    for pdf_path in pdf_files:
        pdf_file = os.path.basename(pdf_path)
        try:
            logger.info(f"Processing {pdf_file}...")
            
            # Load the PDF
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            logger.info(f"Loaded {len(documents)} pages from {pdf_file}")
            
            # Split the document into chunks
            chunks = text_splitter.split_documents(documents)
            
            logger.info(f"Extracted {len(chunks)} chunks from {pdf_file}")
            
            processed_count += 1
            processed_files.append({
                "filename": pdf_file,
                "status": "success",
                "chunks": len(chunks),
                "pages": len(documents)
            })
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file}: {str(e)}")
            failed_count += 1
            processed_files.append({
                "filename": pdf_file,
                "status": "failed",
                "error": str(e)
            })
    
    result = {
        "processed": processed_count,
        "failed": failed_count,
        "files": processed_files
    }
    
    logger.info(f"Document processing complete. Processed: {processed_count}, Failed: {failed_count}")
    return result

if __name__ == "__main__":
    # For testing
    import sys
    if len(sys.argv) > 1:
        dir_path = sys.argv[1]
    else:
        # Try various paths that might work
        possible_paths = [
            r"F:\softograph\rag_langchain_project\data\pdfs",
            "F:\\softograph\\rag_langchain_project\\data\\pdfs",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'pdfs')
        ]
        
        for path in possible_paths:
            print(f"Trying path: {path}")
            if os.path.exists(path):
                dir_path = path
                print(f"Using path: {dir_path}")
                break
        else:
            print("Could not find a valid PDF directory")
            sys.exit(1)
    
    print(f"Testing document processor with directory: {dir_path}")
    result = process_documents(dir_path)
    print(result)