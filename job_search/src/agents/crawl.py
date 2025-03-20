import re
from typing import Any, Dict
from urllib.parse import urlparse

import requests

from src.models.schema import AgentState, CrawlResult
from src.utils.config import DEFAULT_CRAWL_LIMIT, TAVILY_API_KEY


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
        # Call Tavily API for crawling
        response = requests.post(
            "https://dev-api.tavily.com/crawl",
            headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
            json={
                "url": selected_domain,
                "limit": DEFAULT_CRAWL_LIMIT,
                "max_depth": 1,
                "max_breadth": 100,
                "extract_depth": DEFAULT_CRAWL_LIMIT,
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
        # Extract the base domain from selected_domain
        parsed_url = urlparse(selected_domain)
        base_domain_parts = parsed_url.netloc.split(".")

        # Get the main domain (e.g., hibob.com from careers.hibob.com)
        if len(base_domain_parts) >= 2:
            main_domain = ".".join(base_domain_parts[-2:])
        else:
            main_domain = parsed_url.netloc

        # Filter links to identify job posting URLs
        job_posting_links = []
        job_posting_raw_content = {}
        for link in links:
            # Skip anchor links (URLs with #) unless they're part of a job ID
            if "#" in link and not re.search(r"#/jobs?/[a-zA-Z0-9-]+", link):
                continue

            parsed_link = urlparse(link)
            link_domain = parsed_link.netloc

            # Check if it's related to the main domain (including subdomains)
            if main_domain in link_domain:
                path = parsed_link.path.lower()

                # Common job posting patterns in the URL path
                if any(
                    job_indicator in path
                    for job_indicator in [
                        "/jobs/",
                        "/careers/",
                        "/job/",
                        "/position",
                        "/opening",
                        "/vacancy",
                        "/apply",
                        "/employment",
                        "/join-us",
                        "/career",
                    ]
                ):
                    job_posting_links.append(link)
                    if link in raw_content_by_url:
                        job_posting_raw_content[link] = raw_content_by_url[link]

                # Look for UUID or alphanumeric job IDs in the path
                elif re.search(r"/[a-f0-9-]{36}|/\d+(?:-[a-zA-Z0-9-]+)+", path):
                    job_posting_links.append(link)
                    if link in raw_content_by_url:
                        job_posting_raw_content[link] = raw_content_by_url[link]

                # Check for career site platforms in the domain
                elif any(
                    platform in link_domain.lower()
                    for platform in [
                        "careers.",
                        "jobs.",
                        "work.",
                        "join.",
                        "talent.",
                        "hire.",
                        "recruiting.",
                        "greenhouse.io",
                        "lever.co",
                        "workday.com",
                        "breezy.hr",
                        "jobvite.com",
                        "smartrecruiters.com",
                        "bamboohr.com",
                        "workable.com",
                    ]
                ):
                    job_posting_links.append(link)
                    if link in raw_content_by_url:
                        job_posting_raw_content[link] = raw_content_by_url[link]

        # If no job posting links were found, use the careers page itself
        if not job_posting_links and selected_domain:
            job_posting_links = [selected_domain]
            if selected_domain in raw_content_by_url:
                job_posting_raw_content[selected_domain] = raw_content_by_url[
                    selected_domain
                ]

        # Create CrawlResult
        crawl_result = CrawlResult(
            domain=selected_domain,
            links=job_posting_links,
            raw_content=job_posting_raw_content,
        )

        return {"crawl_result": crawl_result}

    except Exception as e:
        return {"error": f"Error in crawling: {str(e)}"}
