import json
from typing import Any, Dict

from langgraph.graph import END, StateGraph

from src.agents.crawl import crawl
from src.agents.domain_search import domain_search
from src.agents.extract import extract
from src.models.schema import AgentState


def create_job_search_agent():
    """
    Create a LangGraph agent for job searching.

    Returns:
        StateGraph: LangGraph agent
    """
    # Create a new graph
    workflow = StateGraph(AgentState)

    # Add nodes to the graph
    workflow.add_node("domain search", domain_search)
    workflow.add_node("web crawl", crawl)
    workflow.add_node("text extraction", extract)

    # Define edges
    # Start with domain search
    workflow.set_entry_point("domain search")

    # Define conditional edges
    def check_error(state: AgentState) -> str:
        """Check if there's an error in the state."""
        if state.error:
            return "error"
        return "next"

    # Add edges
    workflow.add_conditional_edges(
        "domain search", check_error, {"error": END, "next": "web crawl"}
    )

    workflow.add_conditional_edges(
        "web crawl", check_error, {"error": END, "next": "text extraction"}
    )

    # Extract is the final step
    workflow.add_edge("text extraction", END)

    # Compile the graph
    return workflow.compile()


def run_job_search_agent(company_name: str) -> Dict[str, Any]:
    """
    Run the job search agent for a given company.

    Args:
        company_name (str): Name of the company to search for

    Returns:
        Dict[str, Any]: Results of the job search
    """
    # Create the agent
    agent = create_job_search_agent()

    # Save the workflow as a Mermaid PNG
    agent.get_graph(xray=True).draw_mermaid_png(
        output_file_path="job_search_workflow.png"
    )

    # print("Workflow diagram saved as job_search_workflow.png")

    # Initialize the state
    initial_state = AgentState(company_name=company_name)

    # Run the agent
    result = agent.invoke(initial_state)

    # Return the result
    return result


def save_results_to_file(
    result: Dict[str, Any], filename: str = "job_search_results.json"
) -> None:
    """
    Save the results to a file.

    Args:
        result (Dict[str, Any]): Results to save
        filename (str): Name of the file to save to
    """
    # Debug: Print result type and attributes
    # print(f"Result type: {type(result)}")

    # Convert the result to a JSON-serializable format
    serializable_result = {}

    # Handle different result types
    if isinstance(result, dict):
        # print("Result is a dictionary")
        # Convert any Pydantic models in the dictionary to dictionaries
        for key, value in result.items():
            if hasattr(value, "model_dump"):
                serializable_result[key] = value.model_dump()
            elif key == "domain_search_result" and value is not None:
                serializable_result[key] = {
                    "query": value.query,
                }
            elif key == "crawl_result" and value is not None:
                serializable_result[key] = {
                    "base_domain": value.base_domain,
                    "links": value.links,
                }
            elif key == "extract_result" and value is not None:
                serializable_result[key] = {
                    "extracted_jobs": [job.model_dump() for job in value.extracted_jobs]
                }
            else:
                serializable_result[key] = value
    else:
        print(f"Result attributes: {dir(result)}")
        # Add company_name if available
        if hasattr(result, "company_name"):
            serializable_result["company_name"] = result.company_name
        else:
            serializable_result["company_name"] = "Unknown Company"

        # Add error if available
        if hasattr(result, "error"):
            serializable_result["error"] = result.error

        # Add domain search result if available
        if hasattr(result, "domain_search_result") and result.domain_search_result:
            serializable_result["domain_search_result"] = {
                "query": result.domain_search_result.query,
                "top_urls": result.domain_search_result.top_urls,
                "selected_domain": result.domain_search_result.selected_domain,
            }

        # Add crawl result if available
        if hasattr(result, "crawl_result") and result.crawl_result:
            serializable_result["crawl_result"] = {
                "domain": result.crawl_result.domain,
                "links": result.crawl_result.links,
            }

        # Add extract result if available
        if hasattr(result, "extract_result") and result.extract_result:
            serializable_result["extract_result"] = {
                "extracted_jobs": [
                    job.model_dump() for job in result.extract_result.extracted_jobs
                ],
            }

    # Save to file
    with open(filename, "w") as f:
        json.dump(serializable_result, f, indent=2)
