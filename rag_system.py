import os
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class RAGSystem:
    def __init__(self, pdf_dir=None):
        """Initialize the RAG system with Google's Gemini model."""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=self.api_key)
        
        # Set up embedding model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=self.api_key
        )
        
        # Path to vector store - use the same directory as the PDF files
        if pdf_dir:
            self.pdf_dir = pdf_dir
            # Create vector store in the parent directory of pdf_dir
            parent_dir = os.path.dirname(pdf_dir)
            self.vector_store_path = os.path.join(parent_dir, 'vector_store')
        else:
            # Default paths if none provided
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.pdf_dir = os.path.join(base_dir, 'data', 'pdfs')
            self.vector_store_path = os.path.join(base_dir, 'vector_store')
            
        # Make sure vector store directory exists
        os.makedirs(self.vector_store_path, exist_ok=True)
        
        logger.info(f"PDF directory set to: {self.pdf_dir}")
        logger.info(f"Vector store path set to: {self.vector_store_path}")
        
        # Set up LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0.3
        )
        
        # Initialize vector store to None (will be loaded/created when needed)
        self.vector_store = None
    
    def initialize_vector_store(self):
        """Initialize or load the vector store with document embeddings."""
        try:
            # Check if vector store exists
            if os.path.exists(self.vector_store_path) and os.listdir(self.vector_store_path):
                logger.info("Loading existing vector store...")
                self.vector_store = Chroma(
                    persist_directory=self.vector_store_path,
                    embedding_function=self.embeddings
                )
                logger.info(f"Vector store loaded with {self.vector_store._collection.count()} documents")
            else:
                logger.info("Creating new vector store...")
                # Create directory if it doesn't exist
                os.makedirs(self.vector_store_path, exist_ok=True)
                
                # Load and process all PDFs
                documents = []
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    length_function=len,
                )
                
                # Get list of PDF files
                if not os.path.exists(self.pdf_dir):
                    logger.error(f"PDF directory does not exist: {self.pdf_dir}")
                    raise FileNotFoundError(f"PDF directory not found: {self.pdf_dir}")
                
                pdf_files = [f for f in os.listdir(self.pdf_dir) if f.lower().endswith('.pdf')]
                
                if not pdf_files:
                    logger.warning(f"No PDF files found in {self.pdf_dir}")
                    raise ValueError(f"No PDF files found in {self.pdf_dir}")
                
                for pdf_file in pdf_files:
                    pdf_path = os.path.join(self.pdf_dir, pdf_file)
                    logger.info(f"Loading {pdf_file} for vector store...")
                    
                    # Load the PDF
                    loader = PyPDFLoader(pdf_path)
                    pdf_documents = loader.load()
                    
                    # Split the document into chunks
                    chunks = text_splitter.split_documents(pdf_documents)
                    documents.extend(chunks)
                
                logger.info(f"Creating vector store with {len(documents)} chunks...")
                
                # Create vector store
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=self.vector_store_path
                )
                
                # Persist vector store
                self.vector_store.persist()
                logger.info("Vector store created and persisted successfully")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise
    
    def get_retriever(self):
        """Get the retriever from the vector store."""
        if self.vector_store is None:
            self.initialize_vector_store()
        
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
    
    def query(self, query_text):
        """
        Query the RAG system with the given text.
        Returns answer and source documents.
        """
        retriever = self.get_retriever()
        
        # Set up prompt template
        template = """
        You are a helpful AI assistant that provides accurate information based on the given context.
        
        Context:
        {context}
        
        Question:
        {question}
        
        Please provide a detailed answer based only on the provided context. If the context doesn't contain 
        relevant information to answer the question, state that you don't have enough information.
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
        
        # Execute query
        result = qa_chain({"query": query_text})
        
        # Extract source information
        sources = []
        for doc in result["source_documents"]:
            source_info = {
                "content": doc.page_content[:150] + "...",  # First 150 chars
                "metadata": doc.metadata
            }
            sources.append(source_info)
        
        return {
            "answer": result["result"],
            "sources": sources
        }
    
    def get_all_document_content(self):
        """
        Retrieve all document content from the vector store.
        Used for document analysis.
        """
        if self.vector_store is None:
            self.initialize_vector_store()
            
        # This is a simplified version - in a real app, you might want to
        # implement pagination or other optimizations for large document sets
        results = self.vector_store.similarity_search(
            "important information", k=100
        )
        
        return results