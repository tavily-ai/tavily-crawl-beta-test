## 📡 `/crawl` Endpoint – Start a Crawl Job

The `/crawl` endpoint initiates a structured web crawl starting from a specified base URL. The crawler expands from that point like a tree, following internal links across pages. You can control how deep and wide it goes, and guide it to focus on specific sections of the site.

---

### 🔧 Request Parameters

| Parameter         | Type     | Required | Description                                                                                             | Default  |
|------------------|----------|----------|---------------------------------------------------------------------------------------------------------|----------|
| `base_url`       | string   | ✅ Yes    | The root URL to begin the crawl.                                                                        | —        |
| `max_depth`      | integer  | No       | Max depth of the crawl tree. Defines how far from the base URL the crawler can explore.                 | `1`      |
| `max_breadth`    | integer  | No       | Max number of links to follow **per level** of the tree (i.e., per page).                               | `20`     |
| `max_links`      | integer  | No       | Total number of links the crawler will process before stopping.                                         | `50`     |
| `select_paths`   | array    | No       | **Regex patterns** to select only URLs with specific path patterns (e.g., `/docs/.*`, `/api/v1.*`).     | `null`   |
| `select_domains` | array    | No       | **Regex patterns** to select crawling to specific domains or subdomains (e.g., `^docs\.example\.com$`). | `null`   |
| `allow_external` | boolean  | No       | Whether to allow following links that go to external domains.                                           | `false`  |
| `categories`     | array    | No       | Filter URLs using predefined categories like `documentation`, `blog`, `api`, etc.                       | `null`   |


---
### 🔧 Request Parameters 

All parameters are passed in the JSON body of a `POST` request to `/crawl`.

---

#### `base_url` (string, required)

The root URL where the crawl starts.

- **Example**: `"https://example.com"`
- This is the only required field.
- All crawling starts from here.

---

#### `max_depth` (integer, optional)

The maximum **depth** to crawl from the base URL (like the levels of a tree).

- **Default**: `1`
- **Example**: `2`
- A value of `1` means the crawler will follow links on the `base_url`, but not go deeper.

---

#### `max_breadth` (integer, optional)

The maximum number of links to follow **per page** (per level in the crawl tree).

- **Default**: `20`
- **Example**: `10`
- Controls how **wide** the crawl goes at each level.
- If a page has 100 links and `max_breadth = 10`, only the first 10 insightful links are followed.

---

#### `max_links` (integer, optional)

The maximum **total number of links** to crawl in the entire session.

- **Default**: `500`
- **Example**: `1000`
- This is a hard stop for the crawler regardless of depth or breadth.

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
  - `"Enterprise"`
  - `"About"`
  - `"Documentation"`
  - `"Support"`
  - `"Community"`
  - `"Pricing"`
  - `"About"`
  - `"Contact"`

---

> ✅ **You can combine multiple filters together** to guide the crawler very precisely — for example, only crawling blog posts under a specific subdomain with a certain path prefix.

---

### ✅ Success Response (`200 OK`)

On success, the API returns:

```json
{
  "success": true,
  "metadata": {
    "pages_crawled": 120,
    "max_depth_reached": 3,
    "successful_urls": 115,
    "response_time": 2.15
  },
  "config": { /* original request config */ },
  "data": [
    {
      "url": "https://example.com/docs/start",
      "raw_content": "...",
    }
  ]
}
