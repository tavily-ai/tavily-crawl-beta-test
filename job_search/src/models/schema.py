from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DomainSearchResult(BaseModel):
    """Result from domain search step."""

    query: str = Field(description="The search query used")
    top_urls: List[str] = Field(description="List of top URLs from the search results")
    selected_domain: str = Field(description="The selected domain for crawling")


class CrawlResult(BaseModel):
    """Result from crawl step."""

    domain: str = Field(description="The domain that was crawled")
    links: List[str] = Field(description="List of links found during crawling")
    raw_content: Dict[str, str] = Field(
        description="Raw content of each crawled page keyed by URL",
        default_factory=dict,
    )


class JobPosting(BaseModel):
    """Structured job posting information."""

    title: str = Field(description="Job title")
    location: str = Field(description="Job location")
    url: str = Field(description="Original job posting URL")
    benefits: List[str] = Field(description="List of benefits")


class ExtractResult(BaseModel):
    """Result from extract step."""

    extracted_jobs: List[JobPosting] = Field(
        description="List of extracted job postings"
    )
    raw_extractions: Dict[str, Any] = Field(description="Raw extraction data")


class AgentState(BaseModel):
    """State of the agent throughout the workflow."""

    company_name: str = Field(description="Name of the company to search for")
    domain_search_result: Optional[DomainSearchResult] = None
    crawl_result: Optional[CrawlResult] = None
    extract_result: Optional[ExtractResult] = None
    error: Optional[str] = None
