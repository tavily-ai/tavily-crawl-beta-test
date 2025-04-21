## 📡 `/crawl` Endpoint – Start a Crawl Job

The `/crawl` endpoint initiates a structured web crawl starting from a specified base URL. The crawler traverses a site like a graph, following internal links across pages. You can control how deep and wide it goes, and guide it to focus on specific sections of the site.

---

### 🔧 Request Parameters

| Parameter         | Type     | Required | Description                                                                                             | Default  |
|------------------|----------|----------|---------------------------------------------------------------------------------------------------------|----------|
| `url`       | string   | ✅ Yes    | The root URL to begin the crawl.                                                                        | —        |
| `max_depth`      | integer  | No       | Max depth of the crawl tree. Defines how far from the base URL the crawler can explore.                 | `1`      |
| `max_breadth`    | integer  | No       | Max number of links to follow **per level** of the tree (i.e., per page).                               | `20`     |
| `limit`      | integer  | No       | Total number of links the crawler will process before stopping.                                         | `50`     |
| `query`      | string   | No       | Natural language instructions for the crawler                                                           |     —    |
| `select_paths`   | array of strings    | No       | **Regex patterns** to select only URLs with specific path patterns (e.g., `/docs/.*`, `/api/v1.*`).     | `null`   |
| `select_domains` | array of strings    | No       | **Regex patterns** to select crawling to specific domains or subdomains (e.g., `^docs\.example\.com$`). | `null`   |
| `allow_external` | boolean  | No       | Whether to allow following links that go to external domains.                                           | `false`  |
| `categories`     | array of strings    | No       | Filter URLs using predefined categories like `documentation`, `blog`, `api`, etc.                       | `null`   |
| `extract_depth`  | string   | No       | Advanced extraction retrieves more data, including tables and embedded content, with higher success but may increase latency. Options: `"basic"` or `"advanced"`.                                 | `"basic"`|


---
### 🔧 Request Parameters 

All parameters are passed in the JSON body of a `POST` request to `/crawl`.

---

#### `url` (string, required)

The root URL where the crawl starts.

- **Example**: `"https://example.com"`
- This is the only required field.
- All crawling starts from here.

---

#### `max_depth` (integer, optional)

The maximum number of hops from the starting URL the crawler should go. 

- **Default**: `1`
- **Example**:
- tavily.com (depth 0) -> docs.tavily.com (depth 1) -> docs.tavily.com/welcome (depth 2)

Note: Depth is relative and does not necessarily pertain to the file hierarchy of a website. 
- docs.tavily.com (depth 0) -> [tavily.com, docs.tavily.com/welcome] (depth 1) -> status.tavily.com (depth 2) is possible

Warning: Increasing the depth results in an exponential increase in work. Mainting depth <= 3 is recommended.

---

#### `max_breadth` (integer, optional)

The maximum number of links to follow **per page** (per level in the crawl tree).

- **Default**: `20`
- **Example**: `10`
- Controls how **wide** the crawl goes at each level.
- If a page has 100 links and `max_breadth = 10`, only the first 10 insightful links are followed.

---

#### `limit` (integer, optional)

The maximum **total number of links** to crawl in the entire session.

- **Default**: `500`
- **Example**: `1000`
- This is a hard stop for the crawler regardless of depth or breadth.

---

#### `query` (string, optional)

Natural language instructions for the crawler

- **Examples**: `"find documentation for the JavaScript SDK", "all running shoes", "all properties in Lisbon, Portugal"`
- The crawler will intelligently choose links to navigate based on the provided user instructions. 

---

#### `select_paths` (array of strings, optional)

Restricts crawling to URLs that their path matches specific regex patterns.

- **Default**: `null`
- **Example**: `["docs", "blog"]`
- Only URLs that start with one of these paths will be included.

---

#### `select_domains` (array of strings, optional)

Restricts crawling to URLs that their domains/subdomains match specific regex patterns.

- **Default**: `null`
- **Example**: `[".*docs.*", "api"]`
- If set, the crawler will **only follow URLs within these domains**.

---

#### `allow_external` (boolean, optional)

Whether to allow following links that point to **external domains**.

- **Default**: `false`
- **Example**: `true`
- If `true`, the crawler may explore links to completely different domains.

---

#### `categories` (array of strings, optional)

Semantic filtering based on smart URL classification. Only include pages that match one of the given categories.

- **Default**: `null`
- **Example**: `["Documentation", "About"]`
- Supported values:
  - `"Careers"`
  - `"Blog"`
  - `"Documentation"`
  - `"About"`
  - `"Pricing"`
  - `"Community"`
  - `"Developers"`
  - `"Contact"`
  - `"Media"`
 
Note: Categories does not support natural language querying.

#### `extract_depth` (string, optional)

Controls how thoroughly the crawler extracts content from each page.

- **Default**: `"basic"`
- **Options**: `"basic"` or `"advanced"`
- **Example**: `"advanced"`
- `"advanced"` extraction retrieves more data, including tables and embedded content, with higher success but may increase latency.
---

> ✅ **You can combine multiple filters together** to guide the crawler very precisely — for example, only crawling blog posts under a specific subdomain with a certain path prefix.

---

### ✅ Success Response (`200 OK`)

On success, the API returns:

```json
{
    "base_url": "wikipedia.org/wiki/computer",
    "results": [
        {
            "url": "https://en.wikipedia.org/wiki/Computer",
            "raw_content": ...,
            "images": []
        }, ...
    ],
    "response_time" : 1.23,
}
