import argparse
import os
import sys

from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import run_job_search_agent, save_results_to_file


def main():
    """
    Main function to run the job search agent.
    """
    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Job Search Agent")
    parser.add_argument("company_name", help="Name of the company to search for")
    parser.add_argument(
        "--output", "-o", default="job_search_results.json", help="Output file name"
    )
    args = parser.parse_args()

    # Check if API keys are set
    if not os.getenv("TAVILY_API_KEY"):
        print("Error: TAVILY_API_KEY environment variable not set.")
        sys.exit(1)

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        sys.exit(1)

    print(f"Starting job search for {args.company_name}...")

    try:
        # Run the agent
        result = run_job_search_agent(args.company_name)

        # Save the results to a file
        save_results_to_file(result, args.output)

        print(f"Job search completed. Results saved to {args.output}")

        # Print a summary
        if isinstance(result, dict) and "extract_result" in result:
            print("\nSummary:")
            print(f"Total jobs found: {len(result['extract_result'].extracted_jobs)}")

            # Print all job titles and locations
            if result["extract_result"].extracted_jobs:
                print("\nJobs Found:")
                for i, job in enumerate(result["extract_result"].extracted_jobs, 1):
                    print(f"  {i}. {job.title} - {job.location}")
                    print("\n")
                    print(f"    Benefits: {job.benefits}")
                    print("--------------------------------\n")
        elif hasattr(result, "extract_result") and result.extract_result:
            print("\nSummary:")
            print(f"Total jobs found: {len(result.extract_result.extracted_jobs)}")

            # Print all job titles and locations
            if result.extract_result.extracted_jobs:
                print("\nJobs Found:")
                for i, job in enumerate(result.extract_result.extracted_jobs, 1):
                    print(f"  {i}. {job.title} - {job.location}")
                    print("\n")
                    print(f"    Benefits: {job.benefits}")
                    print("--------------------------------\n")
        # Print error if available
        if isinstance(result, dict) and "error" in result:
            print(f"\nError: {result['error']}")
        elif hasattr(result, "error") and result.error:
            print(f"\nError: {result.error}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
