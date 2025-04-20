# Tavily Crawl API - Beta Test

<div align="center">
  <img src="assets/Banner.png" alt="Tavily Banner" width="1000"/>
</div>

## 👋 Welcome to the Tavily Crawl Beta Test!

We're thrilled to have you join us as we roll out our newest endpoint: **Tavily Crawl**! This powerful API allows you to autonomously follow hyperlinks to discover web pages and extract page content with ease.

> 🚀 **Note:** You're part of an exclusive group testing this API before its public release!


## 🕸️ What is Tavily-Crawl?

Tavily Crawl is a site explorer that traverses a website from a given starting point. Traditionally, site crawlers are used to solve the following problems:

**The Needle-in-Haystack:** When a piece of information is deeply embedded within a website, and is unlikely to be discovered via a regular search. e.g. a niche piece of developer documentation or the price of a specific hardware component.

**High-Volume Retrieval of Data:** When a user wants to rapidly identify *all* pages on a site that fit a set of requirements. e.g. a user wants to find *all* the pages on a property listing site that concern properties in a specific area. 

So in order to create a powerful tool that can find you *all* of a certain thing (or a handful of hard-to-find things) within a particular website, we built `/crawl` to have the following characteristics:

**1. High-Quality, Low-Latency Information Retrieval**: Tavily Crawl uses the same powerful technology behind [Tavily Extract](https://docs.tavily.com/documentation/api-reference/endpoint/extract) to fetch links from dynamically rendered pages, single-page applications, and other hard-to-access websites.

**2. Agent-First Intelligent Navigation**: We built a crawler that could be given a goal and would intelligently navigate a website to achieve it. More importantly, we built a crawler that could solve needle-in-haystack problems AND high-volume data retrieval tasks using natural language input. We had agents in mind as we designed Crawl. The `crawl` endpoint can easily be controlled by an agent or be part of a greater agentic workflow. 

**3. Breadth-First, Graph-Faithful**: Tavily Crawl uses the same graph theory frameworks on which the web is built to deliver a *breadth-first* crawler (more on this later). Being able to faithfully reconstruct a complex site graph is how Tavily Crawl consistently returns high-quality results at low-latency.

With these characteristics in mind, we remind you that `crawl` is an unopiniated tool that can mine deep value from websites. In this repository, we'll show you how to use crawl in agentic applications. 

## 👾 Your First Crawl

You can call crawl via API as simple as:

```
curl -X POST https://api.tavily.com/crawl \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "tavily.com",
    "depth": 2,
    "query": "documentation"
  }'
```
Output:

```
"urls":
      "https://docs.tavily.com/",
      "https://docs.tavily.com/api-reference",
      "https://docs.tavily.com/sdk",
      "https://docs.tavily.com/welcome",
      "https://docs.tavily.com/documentation/quickstart",
      ...
```

The `url` parameter is your starting URL. 

The `depth` parameter specifies how many "hops" from the starting URL you want to permit the crawler to go. If it's set at 2, it means the crawler will go from the starting URL to it's linked pages, and then will traverse the pages linked to those pages before returning results.

The `query` parameter allows you to specify your goal in natural language so you can sit back and let the crawler navigate the sitemap. 

Read the [API Documentation](./docs/crawl_api.md) for more details on parameters. Crawl is highly conifgurable, and yet highly effective with only the above three parameters. 

## 📂 Repository Structure

This repository contains everything you need to get started with Tavily Crawl. We have prepared some notebooks and use cases to inspire ideas. Note: the python SDK is still in the works, so we will make direct HTTP POST requests to Tavily's crawl endpoint.

### [API Documentation](./docs)
A md of Tavily Crawl API:

1. [API Documentation](./docs/crawl_api.md) - Crawl API documentation

### [Cookbooks](./cookbooks)
A series of Jupyter notebooks to help you learn and implement Tavily Crawl:

1. [Getting Started](./cookbooks/getting-started.ipynb) - Your first stop to learn the basics of the Crawl endpoint
2. [RAG with Crawl](./cookbooks/crawl-rag.ipynb) - Learn how to crawl webpages and convert them to vector databases for RAG applications
3. [Agentic Crawling](./cookbooks/agentic-crawl.ipynb) - Advanced techniques for autonomous web crawling

### [Job Search Application](./job_search)
A complete [LangGraph](https://github.com/langchain-ai/langgraph) implementation that combines [Tavily Search](https://docs.tavily.com/docs/tavily-api/search), [Tavily Crawl](https://docs.tavily.com/docs/tavily-api/crawl), and [OpenAI](https://openai.com/) to:
- Find all job postings for a company
- Extract key entities and information
- Create structured data from job listings

Check out the [Job Search README](./job_search/README.md) for a detailed description of this use case and system architecture.


## 🚀 Getting Started

```bash
# Clone this repository
git clone https://github.com/tavily-ai/tavily-crawl-beta-test.git

# Navigate to the repository directory
cd tavily-crawl-beta-test

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
python3 -m pip install -r requirements.txt
```

A single virtual environment with these dependencies will work for all notebooks and examples in this repository. 

## 📞 Contact Us

Have questions or feedback? We'd love to hear from you!

- Join our dedicated Slack channel for beta testers
- Email our team directly:
  - [Guy Hartstein](mailto:guyh@tavily.com)
  - [Eyal Ben Barouch](mailto:eyal@tavily.com)
  - [Dean Sacoransky](mailto:deansa@tavily.com)

---

<div align="center">
  <img src="assets/logo_circle.png" alt="Tavily Logo" width="80"/>
  <p>Powered by <a href="https://tavily.com">Tavily</a> - The web API Built for AI Agents</p>
</div>
