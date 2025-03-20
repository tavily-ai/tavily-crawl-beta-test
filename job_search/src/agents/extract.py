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


def extract_entities(url: str, content: str, search_query: str) -> JobPosting:
    """
    Extract structured job posting information from raw content.

    Args:
        url (str): URL of the job posting
        content (str): Raw content of the job posting page
        search_query (str): Search query used to find the job posting

    Returns:
        JobPosting: Structured job posting information
    """
    # Create the chain for job extraction
    chain = job_extraction_prompt | get_llm() | job_posting_parser

    # Run the chain
    result = chain.invoke(
        {
            "url": url,
            "content": content[:4000],  # Limit content size for better performance
            "search_query": search_query,
        }
    )

    # The URL might not be included in the result since it's not part of the extraction
    # So we need to ensure it's set
    result.url = url

    return result


def extract(state: AgentState) -> Dict[str, Any]:
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
        raw_extractions = {}

        # Access the raw content from the crawl result
        raw_content_by_url = (
            state.crawl_result.raw_content
            if hasattr(state.crawl_result, "raw_content")
            else {}
        )

        # Process each link that has raw content available
        for url in links:
            if url in raw_content_by_url and raw_content_by_url[url]:
                content = raw_content_by_url[url]

                # Store raw extraction
                raw_extractions[url] = {
                    "results": [{"url": url, "raw_content": content}]
                }

                try:
                    # Extract job posting information using the already available content
                    job_posting = extract_entities(url, content, search_query)
                    job_postings.append(job_posting)
                except Exception as e:
                    print(f"Error processing content from {url}: {str(e)}")
            else:
                # If we don't have raw content for a link, we might need to fetch it
                # This is a fallback, but since we've refactored to use the raw content
                # from the crawl step, this should be rare
                try:
                    extraction_result = tavily_client.extract(
                        urls=url, extract_depth="advanced"
                    )

                    # Store raw extraction result
                    raw_extractions[url] = extraction_result

                    # Check if extraction was successful
                    if (
                        extraction_result.get("results")
                        and len(extraction_result["results"]) > 0
                        and "raw_content" in extraction_result["results"][0]
                    ):
                        content = extraction_result["results"][0]["raw_content"]

                        # Extract job posting information
                        job_posting = extract_entities(url, content, search_query)
                        job_postings.append(job_posting)

                except Exception as e:
                    print(f"Error extracting from {url}: {str(e)}")

        if not job_postings:
            return {"error": "Failed to extract any job postings."}

        # Create ExtractResult
        extract_result = ExtractResult(
            extracted_jobs=job_postings, raw_extractions=raw_extractions
        )

        return {"extract_result": extract_result}

    except Exception as e:
        import traceback

        print(f"Error in extraction: {str(e)}")
        print(traceback.format_exc())
        return {"error": f"Error in extraction: {str(e)}"}
