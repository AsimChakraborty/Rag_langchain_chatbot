import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionAnsweringAgent:
    def __init__(self, rag_system):
        """Initialize the QA agent with a RAG system."""
        self.rag_system = rag_system
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Set up the Gemini model for the agent
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0.2
        )
    
    def answer_question(self, question):
        """
        Uses the RAG system to answer a question about the documents.
        Returns the answer and the source documents.
        """
        logger.info(f"Answering question: {question}")
        result = self.rag_system.query(question)
        return result


class DocumentAnalysisAgent:
    def __init__(self, rag_system):
        """Initialize the document analysis agent with a RAG system."""
        self.rag_system = rag_system
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Set up the Gemini model for the agent
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0.2
        )
    
    