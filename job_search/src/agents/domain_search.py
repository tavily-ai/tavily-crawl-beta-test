from typing import Any, Dict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient

from src.models.schema import AgentState, DomainSearchResult
from src.utils.config import TAVILY_API_KEY, get_llm
from src.utils.setup_logger import setup_logger

logger = setup_logger("Domain Search")
# Initialize Tavily client
tavily_client = TavilyClient(TAVILY_API_KEY)

# Prompt for domain selection
DOMAIN_SELECTION_PROMPT = """
You are an expert at finding the best career and job domains for companies.

Given the search results below for company "{company_name}", select the most relevant domain 
for finding job postings. Look for:

1. Official company career pages (e.g., careers.company.com)
2. Domains with high relevance to job postings
3. Domains that are likely to contain extractable job content

Here are the top search results:
{search_results}

Select the single best domain URL from the list above.
"""

domain_selection_prompt = ChatPromptTemplate.from_template(DOMAIN_SELECTION_PROMPT)


def get_top_urls(query: str, num_results: int = 3) -> list:
    """
    Perform a Tavily search and return the top URLs from the results.

    Args:
        query (str): The search query
        num_results (int): Number of top URLs to return (default: 3)

    Returns:
        list: List of top URLs from the search results
    """
    try:
        # Execute search with Tavily
        search_results = tavily_client.search(
            query=query, search_depth="advanced", max_results=num_results
        )

        # Extract URLs from results
        top_urls = [result["url"] for result in search_results["results"][:num_results]]
        logger.info(f"Top URLs: {top_urls}")

        return top_urls
    except Exception as e:
        print(f"Error performing Tavily search: {e}")
        return []


def select_best_domain(company_name: str, urls: list) -> str:
    """
    Use LLM to select the best domain for job crawling.

    Args:
        company_name (str): Name of the company
        urls (list): List of URLs to choose from

    Returns:
        str: Selected domain URL
    """
    # Format the search results for the prompt
    formatted_results = "\n".join([f"- {url}" for url in urls])

    # Create the chain for domain selection
    chain = domain_selection_prompt | get_llm() | StrOutputParser()

    # Run the chain
    result = chain.invoke(
        {"company_name": company_name, "search_results": formatted_results}
    )

    # Extract the domain from the result
    # The LLM might provide explanation, so we need to extract just the URL
    for url in urls:
        if url in result:
            return url

    # If no URL is found in the result, return the first URL as a fallback
    return urls[0] if urls else ""


def domain_search(state: AgentState) -> Dict[str, Any]:
    """
    Search for domains related to the company and select the best one for job crawling.

    Args:
        state (AgentState): Current state of the agent

    Returns:
        Dict[str, Any]: Updated state
    """
    company_name = state.company_name
    search_query = f"{company_name} careers"

    try:
        # Get top URLs from Tavily search
        top_urls = get_top_urls(search_query)

        if not top_urls:
            return {"error": f"No URLs found for query: {search_query}"}

        # Select the best domain for job crawling
        selected_domain = select_best_domain(company_name, top_urls)

        # Update the state
        domain_search_result = DomainSearchResult(
            query=search_query, top_urls=top_urls, selected_domain=selected_domain
        )

        return {"domain_search_result": domain_search_result}

    except Exception as e:
        return {"error": f"Error in domain search: {str(e)}"}
