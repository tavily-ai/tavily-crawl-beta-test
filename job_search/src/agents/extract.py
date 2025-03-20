from typing import Dict, Any, List, Tuple
from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.models.schema import AgentState, ExtractResult, JobPosting
from src.utils.config import TAVILY_API_KEY, get_llm, DEFAULT_EXTRACT_DEPTH

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
    partial_variables={"format_instructions": job_posting_parser.get_format_instructions()}
)


def extract_job_posting(url: str, content: str, search_query: str) -> JobPosting:
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
    result = chain.invoke({
        "url": url,
        "content": content[:4000],  # Limit content size for better performance
        "search_query": search_query
    })
    
    # The URL might not be included in the result since it's not part of the extraction
    # So we need to ensure it's set
    result.url = url
    
    return result


def extract_job_postings(links: List[str], search_query: str, max_extractions: int = None) -> Tuple[List[JobPosting], Dict[str, Any]]:
    """
    Extract job postings from a list of links.
    
    Args:
        links (List[str]): List of job posting URLs
        search_query (str): Search query used to find the job postings
        max_extractions (int, optional): Maximum number of extractions to perform. If None, process all links.
    
    Returns:
        Tuple[List[JobPosting], Dict[str, Any]]: List of extracted job postings and raw extractions
    """
    job_postings = []
    raw_extractions = {}
    
    # Determine which links to process
    links_to_extract = links[:max_extractions] if max_extractions is not None else links
    
    # Process links in batches of 20 (Tavily's maximum batch size)
    batch_size = 20
    for i in range(0, len(links_to_extract), batch_size):
        batch_links = links_to_extract[i:i+batch_size]
        
        try:
            # Extract content from multiple URLs at once
            extraction_results = tavily_client.extract(
                urls=batch_links,
                extract_depth=DEFAULT_EXTRACT_DEPTH
            )
            
            # Process each result in the batch
            if extraction_results.get("results"):
                for result in extraction_results["results"]:
                    if "url" in result and "raw_content" in result:
                        url = result["url"]
                        content = result["raw_content"]
                        
                        # Store raw extraction result
                        raw_extractions[url] = {"results": [result]}
                        
                        try:
                            # Extract job posting information
                            job_posting = extract_job_posting(url, content, search_query)
                            job_postings.append(job_posting)
                        except Exception as e:
                            print(f"Error processing extracted content from {url}: {str(e)}")
            
        except Exception as e:
            print(f"Error extracting batch of links: {str(e)}")
            # If batch extraction fails, fall back to individual extraction
            for link in batch_links:
                try:
                    # Extract content from a single URL
                    extraction_result = tavily_client.extract(
                        urls=link,
                        extract_depth=DEFAULT_EXTRACT_DEPTH
                    )
                    
                    # Store raw extraction result
                    raw_extractions[link] = extraction_result
                    
                    # Check if extraction was successful
                    if (extraction_result.get("results") and 
                        len(extraction_result["results"]) > 0 and 
                        "raw_content" in extraction_result["results"][0]):
                        
                        content = extraction_result["results"][0]["raw_content"]
                        
                        # Extract job posting information
                        job_posting = extract_job_posting(link, content, search_query)
                        job_postings.append(job_posting)
                    
                except Exception as e:
                    print(f"Error extracting from {link}: {str(e)}")
    
    return job_postings, raw_extractions


def extract(state: AgentState) -> Dict[str, Any]:
    """
    Extract job postings from the crawled links.
    
    Args:
        state (AgentState): Current state of the agent
    
    Returns:
        Dict[str, Any]: Updated state
    """
    # Debug: Print state type and attributes
    #print(f"State type: {type(state)}")
    #print(f"State attributes: {dir(state)}")
    
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
        
        print(f"Using search query: {search_query}")
        
        # Extract job postings - no maximum limit
        job_postings, raw_extractions = extract_job_postings(links, search_query)
        
        if not job_postings:
            return {"error": "Failed to extract any job postings."}
        
        # Create ExtractResult
        extract_result = ExtractResult(
            extracted_jobs=job_postings,
            raw_extractions=raw_extractions
        )
        
        return {"extract_result": extract_result}
    
    except Exception as e:
        import traceback
        print(f"Error in extraction: {str(e)}")
        print(traceback.format_exc())
        return {"error": f"Error in extraction: {str(e)}"} 