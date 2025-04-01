# Deep Job Search Agent

This project uses a LangGraph agent with Tavily to search, crawl, and extract job posting data from the web. It leverages OpenAI's LLM to extract key entities from the job postings like job title, location, and benefits.

## Configuration

You can modify the application configuration in `src/utils/config.py`:

- `DEFAULT_MODEL`: The OpenAI model to use
- `DEFAULT_CRAWL_LIMIT`: The maximum number of pages to crawl -- set to 100 by default...feel free to play around.
- `DEFAULT_EXTRACT_DEPTH`: Set to `advanced` to retrieve more data, including tables and embedded content, with higher success.


## Features

- **Tavily `/Search`**: Identifies the optimal job posting domain for any specified company
- **Tavily `/Crawl`**: Intelligently navigates the career domain to discover all job posting links and extract relevant content
  - Utilizes `categories` semantic filtering parameter to precisely target job postings
- **Entity Recognition**: Extracts structured data (job titles, locations, benefits) from web content using OpenAI's LLM capabilities
- **LangGraph Orchestration**: Coordinates the entire workflow through a sophisticated agent-based architecture

Note: control the number of pages to crawl in `src/utils/config.py` with the `DEFAULT_CRAWL_LIMIT` variable. Currently set to 100 to limit api consumption.


## Agent Workflow

![Agent Workflow](agentic_workflow_diagram.png)

## Setup

1. Clone the repository
2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install dependencies
```bash
python3 -m pip install -r requirements.txt
```
3. Create a `.env` file with your API keys:
   ```
   TAVILY_API_KEY=your_tavily_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

Run the agent with a company name from the root directory of this repo. For example:
```bash

python3 job_search/src/main.py "Wiz"
```

## Example Output

The results will be saved to `job_search_results.json` by default. 

The agent produces a structured JSON output containing the Tavily Search result ()`domain_search_result`), Tavily Crawl result (`crawl_result`), and agent output (`extracted job entities`). Here's a sample of what the output looks like:

```json
{
  "company_name": "Wiz",
  "domain_search_result": {
    "query": "Wiz careers",
    "top_urls": [
      "https://www.wiz.io/careers",
      "https://jobs.a16z.com/jobs/wiz",
      "https://www.linkedin.com/company/wizsecurity/jobs"
    ],
    "selected_domain": "https://www.wiz.io/careers"
  },
  "crawl_result": {
    "domain": "https://www.wiz.io/careers",
    "links": [
      "https://wiz.io/careers/job/4449112006/hris-analystgh_jid=4449112006",
      "https://wiz.io/careers/job/4005273006/dev-ops-engineergh_jid=4005273006",
      "https://wiz.io/careers/job/4004237006/product-managergh_jid=4004237006",
      "https://wiz.io/careers/job/4408878006/data-engineergh_jid=4408878006",
      // ... more links ...
    ]
  },
  "extract_result": {
    "extracted_jobs": [
      {
        "title": "HRIS Analyst",
        "location": "Tel Aviv, IL",
        "url": "https://wiz.io/careers/job/4449112006/hris-analystgh_jid=4449112006",
        "benefits": [
          "Equal opportunity employer",
          "Diverse and inclusive workplace",
          "Opportunity to work with a global team",
          "Freedom to think creatively and dream big"
        ]
      },
      {
        "title": "DevOps Engineer",
        "location": "Tel Aviv",
        "url": "https://wiz.io/careers/job/4005273006/dev-ops-engineergh_jid=4005273006",
        "benefits": [
          "Equal opportunity employer",
          "Innovative, high-performance team",
          "Work with cutting-edge technologies",
          "Dynamic and agile environment",
          "Freedom to think creatively and dream big"
        ]
      },
      // ... more jobs ...
    ]
  }
}
```

## Project Structure

- `src/agents/`: Contains the agent nodes (domain_search, crawl, extract)
- `src/models/`: Contains the Pydantic models for structured data
- `src/utils/`: Contains utility functions and configuration
- `src/main.py`: Main script to run the agent