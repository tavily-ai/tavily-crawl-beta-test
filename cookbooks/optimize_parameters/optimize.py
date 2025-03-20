"""
Main implementation of the TavilySearchTool.
"""

import json
import os
from typing import Optional

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# from tavily import TavilyClient
from langchain_openai import ChatOpenAI

from optimize_parameters.prompts import TAVILY_PARAMETER_PROMPT
from optimize_parameters.schemas import (
    TavilySearchParameters,
)

load_dotenv()


class OptimizeParameters:
    """
    A tool for optimizing and executing Tavily API calls based on natural language instructions.
    """

    def __init__(
        self,
        model: str = "gemma2-9b-it",
        provider: str = "groq",
        tavily_api_key: Optional[str] = None,
    ):
        """
        Initialize the TavilySearchTool.

        Args:
            model: Model name to use - must be a supported CHAT model by the provider (e.g., "gpt-4o-mini", "gemma2-9b-it")
            provider: Model provider - either "openai" or "groq"
            tavily_api_key: The Tavily API key (defaults to TAVILY_API_KEY env var)
        """
        self.model = model
        self.provider = provider.lower()
        # self.tavily_api_key = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        # Initialize the appropriate LLM client based on provider
        if self.provider == "groq":
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY environment variable not set")

            self.llm = ChatGroq(
                model=model,
                temperature=0,
                max_tokens=None,
                timeout=2,
                max_retries=0,
                api_key=groq_api_key,
            )
        elif self.provider == "openai":
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            self.llm = ChatOpenAI(model=model, temperature=0, api_key=openai_api_key)
        else:
            raise ValueError(
                f"Unsupported provider: {provider}. Use 'openai' or 'groq'"
            )

    def optimize_parameters(self, instruction: str) -> TavilySearchParameters:
        """
        Optimize Tavily search parameters based on a natural language instruction.

        Args:
            instruction: The natural language instruction

        Returns:
            TavilySearchParameters: Optimized parameters for the Tavily API
        """
        # Create the prompt with the instruction
        prompt = TAVILY_PARAMETER_PROMPT.format(instruction=instruction)

        # Determine which prompting approach to use based on the provider
        if self.provider == "groq":
            # Use structured output for Groq models
            response = self.llm.with_structured_output(TavilySearchParameters).invoke(
                prompt
            )
            return response
        else:
            # Use function calling for OpenAI models
            function_schema = TavilySearchParameters.model_json_schema()
            function_def = {
                "name": "optimize_tavily_parameters",
                "description": "Optimize parameters for a Tavily API search based on a natural language instruction",
                "parameters": function_schema,
            }

            # Call the LLM with function calling
            response = self.llm.invoke(
                prompt,
                functions=[function_def],
                function_call={"name": "optimize_tavily_parameters"},
            )

            # Extract and parse the function arguments
            function_args = json.loads(
                response.additional_kwargs["function_call"]["arguments"]
            )

            # Convert to a Pydantic model
            return TavilySearchParameters(**function_args)

    # def search_tavily(self, parameters: TavilySearchParameters) -> Dict[str, Any]:
    #     """
    #     Execute a search with the Tavily API using the provided parameters.

    #     Args:
    #         parameters: The parameters to use for the search

    #     Returns:
    #         Dict[str, Any]: The raw search results from the Tavily API
    #     """
    #     # Convert parameters to a dictionary and directly pass to Tavily API
    #     # This simplifies the conversion process
    #     params_dict = parameters.model_dump(exclude_none=True)

    #     # Execute the search
    #     return self.tavily_client.search(**params_dict)

    # def optimize_and_search(self, instruction: str) -> TavilySearchResponse:
    #     """
    #     Process a natural language instruction and execute a Tavily search.
    #
    #     Args:
    #         instruction: The natural language instruction
    #
    #     Returns:
    #         TavilySearchResponse: The search results
    #     """
    #     # Optimize parameters based on the instruction
    #     parameters = self.optimize_parameters(instruction)
    #
    #     # Execute the search
    #     search_results = self.search_tavily(parameters)
    #
    #     # Convert raw results to TavilySearchResult objects
    #     result_objects = []
    #     for result in search_results.get("results", []):
    #         result_objects.append(TavilySearchResult(**result))
    #
    #     # Create and return the response object
    #     return TavilySearchResponse(
    #         results=result_objects,
    #         query=search_results.get("query", parameters.query),
    #         answer=search_results.get("answer"),
    #         metadata=search_results.get("metadata", {})
    #     )
