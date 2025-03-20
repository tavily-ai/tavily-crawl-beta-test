# Job Search LangGraph Agent

This project uses a LangGraph agent with Tavily to search, crawl, and extract job posting data from the web. It leverages OpenAI's LLM to extract key information like job titles and locations.

## Features

- Tavily search: Find the best job posting domain for a given company
- Tavily crawl: Crawl the career domain to find all nested job posting links
- Tavily extraction: Extract text from the job posting links.
- Named entity recognition: Extract entities (title and location) from scraped web content using LLM

Note: control the number of pages to crawl in `src/utils/config.py` with the `DEFAULT_CRAWL_LIMIT` variable. Currently set to 5 to limit api consumption.


## Agent Workflow

![Agent Workflow](job_search_workflow.png)

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

Run the agent with a company name:

For example:
```bash
python3 src/main.py "HiBob"
```

## Example Output

The results will be saved to `job_search_results.json` by default. 

The agent produces a structured JSON output containing the search results, crawled links, and extracted job information. Here's a sample of what the output looks like:

```json
{
  "company_name": "HiBob",
  "domain_search_result": {
    "query": "HiBob careers",
    "top_urls": [
      "https://www.hibob.com/careers/",
      "https://uk.linkedin.com/company/hibob/jobs",
      "https://www.indeed.com/cmp/Hibob"
    ],
    "selected_domain": "https://www.hibob.com/careers/"
  },
  "crawl_result": {
    "domain": "https://www.hibob.com/careers/",
    "links": [
      "https://hibob-e013d08dd01044.careers.hibob.com/jobs/98c12943-f07c-4b0b-9bc6-3f1de303c019",
      "https://hibob-e013d08dd01044.careers.hibob.com/jobs/3a5b4e08-40b0-425d-b41f-f18e5d85ea0e",
      // ... more links ...
    ]
  },
  "extract_result": {
    "extracted_jobs": [
      {
        "title": "Procurement Buyer –SaaS & IT Hardware",
        "location": "IL, Israel",
        "url": "https://hibob-e013d08dd01044.careers.hibob.com/jobs/98c12943-f07c-4b0b-9bc6-3f1de303c019"
      },
      {
        "title": "Senior Data Engineer",
        "location": "IL, Israel",
        "url": "https://hibob-e013d08dd01044.careers.hibob.com/jobs/3a5b4e08-40b0-425d-b41f-f18e5d85ea0e"
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

## Configuration

You can modify the configuration in `src/utils/config.py`:

- `DEFAULT_MODEL`: The OpenAI model to use
- `DEFAULT_CRAWL_LIMIT`: The maximum number of pages to crawl
- `MAX_EXTRACTIONS_PER_RUN`: The maximum number of job postings to extract

This repository also contains two Jupyter notebooks demonstrating advanced web crawling techniques:

## mastering-the-crawl-endpoint.ipynb
- Deep dive into Firecrawl's crawl endpoint with comprehensive features and optimizations
- Explores different parameters and configuration options

## tavily-firecrawl.ipynb
- Integrates Tavily Search with Firecrawl's crawl endpoint and Tavily Extract
- Showcases a complete workflow for finding and extracting job postings for a company
- Combines search, crawling, and extraction capabilities for data collection
