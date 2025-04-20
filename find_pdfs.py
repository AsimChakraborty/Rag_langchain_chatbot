import os
import sys

def find_pdfs():
    """
    Diagnostic tool to find PDF files in a directory.
    """
    # Check the specified folder
    specified_path = r"F:/softograph/rag_langchain_project/data/pdfs"
    print(f"Looking for PDFs in specified path: {specified_path}")
    
    # Check if directory exists
    if os.path.exists(specified_path):
        print(f"✓ Directory exists: {specified_path}")
        files = os.listdir(specified_path)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        
        if pdf_files:
            print(f"✓ Found {len(pdf_files)} PDF files:")
            for pdf in pdf_files:
                full_path = os.path.join(specified_path, pdf)
                size_kb = os.path.getsize(full_path) / 1024
                print(f"   - {pdf} ({size_kb:.2f} KB)")
        else:
            print("✗ No PDF files found in this directory")
            print("  Files in directory:")
            if files:
                for file in files:
                    print(f"   - {file}")
            else:
                print("   (Directory is empty)")
    else:
        print(f"✗ Directory does not exist: {specified_path}")
    
   
if __name__ == "__main__":
    find_pdfs()