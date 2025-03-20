import asyncio
from typing import Any, Dict

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient

from src.models.schema import AgentState, ExtractResult, JobPosting
from src.utils.config import TAVILY_API_KEY, get_llm

# Initialize Tavily client
tavily_client = TavilyClient(TAVILY_API_KEY)

# Create a parser for JobPosting
job_posting_parser = PydanticOutputParser(pydantic_object=JobPosting)

# Prompt for job posting extraction
JOB_EXTRACTION_PROMPT = """
You are an expert at extracting structured job posting information from raw HTML or text content.

Below is the content of a job posting page related to the search query "{search_query}". Extract the following information:
- Job title
- Job location (city, country, or remote status)
- Benefits

URL: {url}

Content:
{content}

{format_instructions}

If any field is not available, use "Unknown" for that field.
"""

job_extraction_prompt = ChatPromptTemplate.from_template(
    template=JOB_EXTRACTION_PROMPT,
    partial_variables={
        "format_instructions": job_posting_parser.get_format_instructions()
    },
)


async def extract_entities_async(
    url: str, content: str, search_query: str
) -> JobPosting:
    """
    Extract structured job posting information from raw content.

    Args:
        url (str): URL of the job posting
        content (str): Raw content of the job posting page
        search_query (str): Search query used to find the job posting

    Returns:
        JobPosting: Structured job posting information
    """
    # Create the chain for job extraction (use async compatible LLM)
    llm = get_llm()  # Make sure get_llm returns an async-compatible model
    chain = job_extraction_prompt | llm | job_posting_parser

    # Run the chain asynchronously
    result = await chain.ainvoke(
        {
            "url": url,
            "content": content[:4000],
            "search_query": search_query,
        }
    )

    result.url = url
    return result


async def extract_async(state: AgentState) -> Dict[str, Any]:
    """
    Extract job posting entities from the raw content of the crawled links.

    Args:
        state (AgentState): Current state of the agent

    Returns:
        Dict[str, Any]: Updated state
    """
    # Check if crawl was successful
    if not state.crawl_result:
        return {"error": "Crawl result not available. Run crawl first."}

    links = state.crawl_result.links

    if not links:
        return {"error": "No links found in crawl result."}

    try:
        # Get search query from domain search result
        search_query = "Unknown Company"
        if hasattr(state, "domain_search_result") and state.domain_search_result:
            search_query = state.domain_search_result.query

        # Process job postings from the raw content already available from crawl step
        job_postings = []

        # Access the raw content from the crawl result
        raw_content_by_url = (
            state.crawl_result.raw_content
            if hasattr(state.crawl_result, "raw_content")
            else {}
        )

        # Create tasks for all URLs with content
        tasks = []
        for url in links:
            if url in raw_content_by_url and raw_content_by_url[url]:
                content = raw_content_by_url[url]
                # Add task
                task = extract_entities_async(url, content, search_query)
                tasks.append(task)

        # Execute all tasks concurrently
        if tasks:
            job_postings = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions
            job_postings = [jp for jp in job_postings if not isinstance(jp, Exception)]

        if not job_postings:
            return {"error": "Failed to extract any job postings."}

        # Create ExtractResult
        extract_result = ExtractResult(extracted_jobs=job_postings)

        return {"extract_result": extract_result}

    except Exception as e:
        import traceback

        print(f"Error in extraction: {str(e)}")
        print(traceback.format_exc())
        return {"error": f"Error in extraction: {str(e)}"}


# Create a synchronous wrapper for compatibility
def extract(state: AgentState) -> Dict[str, Any]:
    return asyncio.run(extract_async(state))
