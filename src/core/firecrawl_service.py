import os

# Disable SSL verification before importing any network libraries
try:
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

# Also try using certifi if available
try:
    import certifi
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    os.environ['CURL_CA_BUNDLE'] = ''
except Exception:
    pass

from firecrawl import FirecrawlApp
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.store import store


def get_firecrawl_app() -> FirecrawlApp:
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY is missing in environment variables.")
    return FirecrawlApp(api_key=api_key)

def generate_search_queries(topic: str) -> list[str]:
    """יוצר שאילתות חיפוש מורחבות ומגוונות עבור Firecrawl"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    prompt = (
        f"You are a search assistant. The user wants to search for: '{topic}'.\n"
        f"Generate 3 short, effective, broad web search queries (2-4 words each) "
        f"that will easily find results on search engines.\n"
        f"Do NOT include future years, wordy descriptions, or quotes.\n"
        f"Return ONLY the 3 queries separated by newlines."
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
    return queries if queries else [topic]

def search_and_index_web(topic: str, max_results_per_query: int = 2) -> list[str]:
    """Search web via Firecrawl with comprehensive error handling."""
    try:
        app = get_firecrawl_app()
    except Exception as e:
        print(f"❌ Could not initialize Firecrawl: {e}", flush=True)
        return []
    
    try:
        queries = generate_search_queries(topic)
    except Exception as e:
        print(f"❌ Error generating search queries: {e}", flush=True)
        return []
    
    print(f"🔍 Generated search queries: {queries}", flush=True)

    added_sources = []
    visited_urls = set()

    for query in queries:
        try:
            print(f"🌐 Searching Firecrawl for: '{query}'...", flush=True)
            search_response = app.search(query, limit=max_results_per_query)
            
            # Extract results from SearchData object
            results = []
            if isinstance(search_response, dict):
                # If it's a dict, try standard response keys
                results = search_response.get("data", []) or search_response.get("results", [])
            elif hasattr(search_response, "web"):
                # Firecrawl returns SearchData with .web attribute for web search results
                results = search_response.web if search_response.web else []
            elif hasattr(search_response, "data"):
                results = search_response.data if search_response.data else []
            elif hasattr(search_response, "results"):
                results = search_response.results if search_response.results else []
            
            print(f"📄 Found {len(results)} search results for '{query}'.", flush=True)

            for item in results:
                try:
                    # Extract URL and title from SearchResultWeb object or dict
                    if isinstance(item, dict):
                        url = item.get("url")
                        title = item.get("title", "Web Source")
                    else:
                        # Assume it's an object with attributes (SearchResultWeb)
                        url = getattr(item, "url", None)
                        title = getattr(item, "title", "Web Source")

                    if not url or url in visited_urls:
                        continue
                    visited_urls.add(url)

                    print(f"🕷️ Scraping URL: {url}", flush=True)
                    scrape_response = app.scrape_url(url, formats=["markdown"])

                    # Extract markdown content
                    content = None
                    if isinstance(scrape_response, dict):
                        content = scrape_response.get("markdown")
                    elif hasattr(scrape_response, "markdown"):
                        content = scrape_response.markdown

                    if content and len(content.strip()) > 100:
                        source_name = f"[Web] {title} ({url})"
                        source = store.add(name=source_name, content=content)
                        added_sources.append(source.name)
                        print(f"✅ Successfully indexed: {source_name}", flush=True)
                except Exception as e:
                    print(f"⚠️  Error processing search result: {e}", flush=True)
                    continue

        except Exception as e:
            print(f"❌ Error processing query '{query}': {type(e).__name__}: {str(e)[:100]}", flush=True)
            continue

    if not added_sources:
        print(f"⚠️  No web sources were successfully indexed for '{topic}'", flush=True)

    return added_sources