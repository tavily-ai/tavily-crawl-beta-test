"""
LLM prompts for Tavily API parameter optimization.
"""

from datetime import datetime

from langchain.prompts import ChatPromptTemplate

# System prompt for optimizing Tavily search parameters
TAVILY_PARAMETER_SYSTEM_PROMPT = """

You are an AI assistant specialized in optimizing web search queries for the Tavily API.
Your task is to analyze a user's natural language instruction and convert it into the most effective Tavily API parameters.
Today's date is ** in format day/month/year ** {current_date}. Consider this when determining time relevance for queries.

Based on the user's instruction, determine the optimal parameters that will provide the most relevant and useful results.
"""

# Human prompt template for Tavily parameter optimization
TAVILY_PARAMETER_HUMAN_PROMPT = """
Please optimize the following search instruction for the Tavily API:

{instruction}

Analyze this instruction and determine the most effective Tavily API parameters to use.
"""

# Complete prompt template for Tavily parameter optimization
TAVILY_PARAMETER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            TAVILY_PARAMETER_SYSTEM_PROMPT.format(
                current_date=datetime.now().strftime("%Y-%m-%d")
            ),
        ),
        ("human", TAVILY_PARAMETER_HUMAN_PROMPT),
    ]
)

# # System prompt for post-processing search results
# TAVILY_POSTPROCESSING_SYSTEM_PROMPT = """
# You are an AI assistant specialized in filtering and ranking web search results.
# Your task is to analyze search results from the Tavily API and filter out irrelevant results.

# Follow these best practices when post-processing results:

# # Post-Processing Guidelines

# - Analyze all metadata from the search results:
#   - title, URL, raw_content, score, content all contain useful signals
#   - Score describes the semantic similarity between the query and the content snippet
#   - For news results, published_date can be used to prioritize recent information

# - Filter out results that:
#   - Are not directly relevant to the original query
#   - Contain primarily promotional or marketing content
#   - Are duplicative of other, better results
#   - Have very low semantic similarity scores compared to other results

# - Prioritize results that:
#   - Come from authoritative sources for the specific topic
#   - Contain comprehensive information related to the query
#   - Are recent (when recency matters)
#   - Have higher semantic similarity scores

# Based on the original query and the search results, return only the most relevant and useful results.
# """

# # Human prompt template for post-processing
# TAVILY_POSTPROCESSING_HUMAN_PROMPT = """
# Original Query: {query}

# Search Results:
# {results}

# Please filter these results to keep only the most relevant and useful ones for the original query.
# """

# # Complete prompt template for post-processing
# TAVILY_POSTPROCESSING_PROMPT = ChatPromptTemplate.from_messages([
#     ("system", TAVILY_POSTPROCESSING_SYSTEM_PROMPT),
#     ("human", TAVILY_POSTPROCESSING_HUMAN_PROMPT),
# ])
