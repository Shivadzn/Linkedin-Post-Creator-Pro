"""
LLM helper module for the LinkedIn Post Generator.
Provides a clean interface to the Groq API with error handling and configuration.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Global LLM client instance
_llm_client: Optional[ChatGroq] = None


def get_groq_client() -> ChatGroq:
    """
    Get or create a Groq LLM client instance.
    
    Returns:
        ChatGroq: Configured LLM client
        
    Raises:
        ValueError: If API key is not configured
    """
    global _llm_client
    
    if _llm_client is None:
        settings = get_settings()
        
        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment variables. "
                "Please set it in your .env file or environment."
            )
        
        try:
            _llm_client = ChatGroq(
                model=settings.groq_model,
                api_key=settings.groq_api_key
            )
            logger.info(f"Initialized Groq client with model: {settings.groq_model}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise
    
    return _llm_client


def reset_llm_client():
    """Reset the global LLM client instance (useful for testing)."""
    global _llm_client
    _llm_client = None


def test_llm_connection() -> bool:
    """
    Test the LLM connection with a simple query.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        client = get_groq_client()
        response = client.invoke("Hello, this is a test message.")
        logger.info("LLM connection test successful")
        return True
    except Exception as e:
        logger.error(f"LLM connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the LLM connection
    if test_llm_connection():
        print("✅ LLM connection successful!")
    else:
        print("❌ LLM connection failed!")