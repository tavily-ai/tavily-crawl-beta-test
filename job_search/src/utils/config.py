import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model configuration
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.0


# Create OpenAI model instances
def get_llm(model_name=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE):
    """Get an OpenAI LLM instance with the specified parameters."""
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=OPENAI_API_KEY,
        request_timeout=60,
        streaming=False,
    )


# Crawl configuration
DEFAULT_CRAWL_LIMIT = 30
DEFAULT_CRAWL_FORMATS = ["links"]

# Extract configuration
DEFAULT_EXTRACT_DEPTH = "advanced"
MAX_CONTENT_CHARS = 8000  # Maximum characters to use for content extraction
