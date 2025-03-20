"""
Pydantic models for Tavily API parameters and responses.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class TavilySearchParameters(BaseModel):
    """
    Pydantic model for Tavily search parameters.
    """
    query: str = Field(
        description="The search query from the user to the Tavily API"
    )
    include_domains: Optional[List[str]] = Field(
        default=[],
        description="""A list of domains to restrict search results to.

        Use this parameter when:
        1. The user explicitly requests information from specific websites (e.g., "Find climate data from nasa.gov")
        2. The user mentions an organization or company without specifying the domain (e.g., "Find information about iPhones from Apple")

        In both cases, you should determine the appropriate domains (e.g., ["nasa.gov"] or ["apple.com"]) and set this parameter.

        Results will ONLY come from the specified domains - no other sources will be included.
        Default is None (no domain restriction).
        """
    )
    exclude_domains: Optional[List[str]] = Field(
        default=[],
        description="""A list of domains to exclude from search results.
        
        IMPORTANT: ONLY use this parameter when:
        1. The user explicitly requests to avoid certain websites (e.g., "Find information about climate change but not from twitter.com")
        2. The user mentions not wanting results from specific organizations without naming the domain (e.g., "Find phone reviews but nothing from Apple")

        In both cases, you should determine the appropriate domains to exclude (e.g., ["twitter.com"] or ["apple.com"]) and set this parameter.

        Results will filter out all content from the specified domains.
        Default is None (no domain exclusion).
        """
    )
    include_images: bool = Field(
        default=False,
        description="""Determines if the search returns relevant images along with text results.
        
        Leave as False (default) for most informational queries where text is sufficient.
        
        Set to True when the user explicitly requests visuals or when images would 
        significantly enhance understanding (e.g., "Show me what black holes look like," 
        "Find pictures of Renaissance art").
        """
    )
    include_image_descriptions: bool = Field(
        default=False,
        description="""Whether to include descriptions of images in the search results
        IMPORTANT: This parameter ONLY functions when 'include_images' is set to True. 
        If 'include_images' is False or not specified, this parameter can NOT be set to True.
        """
    )
    topic: Optional[Literal["news", "finance", "general"]] = Field(
        default="general",
        description="""Specifies search category for optimized results.
   
        Use "general" (default) for most queries, INCLUDING those with terms like 
        "latest," "newest," or "recent" when referring to general information.

        Use "finance" for markets, investments, economic data, or financial news.

        Use "news" ONLY for politics, sports, or major current events covered by 
        mainstream media - NOT simply because a query asks for "new" information.
        """
    )
    time_range: Optional[Literal["day", "week", "month", "year"]] = Field(
        default=None,
        description="""Limits results to content published within a specific timeframe.
        
        ONLY set this when the user explicitly mentions a time period 
        (e.g., "latest AI news," "articles from last week").
        
        For less popular or niche topics, use broader time ranges 
        ("month" or "year") to ensure sufficient relevant results.
   
        Options: "day" (24h), "week" (7d), "month" (30d), "year" (365d).
        
        Default is None.
        """
    )


class TavilySearchResult(BaseModel):
    """
    Pydantic model for a single Tavily search result.
    """
    url: str = Field(description="URL of the search result")
    title: str = Field(description="Title of the search result")
    content: str = Field(description="NLP-based snippet of the web page")
    score: float = Field(description="Semantic similarity score between query and content")
    raw_content: Optional[str] = Field(default=None, description="Raw content of the web page if requested")
    published_date: Optional[str] = Field(default=None, description="Published date for news articles")

class TavilySearchResponse(BaseModel):
    """
    Pydantic model for the Tavily search response.
    """
    results: List[TavilySearchResult] = Field(description="List of search results")
    query: str = Field(description="The search query from the user")
    answer: Optional[str] = Field(default=None, description="AI-generated answer if requested")
    follow_up_questions: Optional[List[str]] = Field(default=None, description="Follow-up questions that can be used to refine the search")
    images: Optional[List[Dict[str, str]]] = Field(default=None, description="List of image information including URLs and descriptions if requested")
    response_time: Optional[float] = Field(default=None, description="Time taken to generate the response")