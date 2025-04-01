from typing import Any, Dict
from urllib.parse import urlparse

import requests

from src.models.schema import AgentState, CrawlResult
from src.utils.config import (
    DEFAULT_CRAWL_LIMIT,
    DEFAULT_EXTRACT_DEPTH,
    TAVILY_API_KEY,
)


def crawl(state: AgentState) -> Dict[str, Any]:
    """
    Crawl the selected domain to find job postings.

    Args:
        state (AgentState): Current state of the agent

    Returns:
        Dict[str, Any]: Updated state
    """
    # Check if domain search was successful
    if not state.domain_search_result:
        return {"error": "Domain search result not available. Run domain search first."}

    selected_domain = state.domain_search_result.selected_domain

    try:
        # Extract the base domain from selected_domain
        parsed_url = urlparse(selected_domain)
        base_domain_parts = parsed_url.netloc.split(".")

        if len(base_domain_parts) >= 2:
            main_domain = ".".join(base_domain_parts[-2:])
        else:
            main_domain = parsed_url.netloc

        # Call Tavily API for crawling
        response = requests.post(
            "https://api.tavily.com/crawl",
            headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
            json={
                "url": selected_domain,
                "limit": DEFAULT_CRAWL_LIMIT,
                "max_depth": 3,
                "max_breadth": 100,
                "extract_depth": DEFAULT_EXTRACT_DEPTH,
                "allow_external": True,
                "categories": ["Careers"],
            },
        )

        # Check if the request was successful
        if response.status_code != 200:
            return {
                "error": f"Error in crawling: API returned status code {response.status_code}"
            }

        # Parse the response
        crawl_result_data = response.json()

        # Extract links and raw content from the crawl result
        links = []
        raw_content_by_url = {}
        if "data" in crawl_result_data:
            pages = crawl_result_data["data"]
            for page in pages:
                if "url" in page:
                    links.append(page["url"])
                    # Store raw content for each URL
                    if "raw_content" in page:
                        raw_content_by_url[page["url"]] = page["raw_content"]

        print(f"Crawled {len(links)} pages")
        # print(links)

        # Create CrawlResult
        crawl_result = CrawlResult(
            domain=selected_domain,
            links=links,
            raw_content=raw_content_by_url,
        )

        return {"crawl_result": crawl_result}

    except Exception as e:
        return {"error": f"Error in crawling: {str(e)}"}
