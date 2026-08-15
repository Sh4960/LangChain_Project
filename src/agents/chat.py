


# from dataclasses import dataclass

# from langchain.agents import create_agent
# from langchain_core.tools import tool
# from langgraph.checkpoint.memory import InMemorySaver

# from core.sources import format_docs
# from core.store import SourceStore, store
# from core.firecrawl_service import search_and_index_web

# @dataclass
# class Answer:
#     text: str
#     sources: list[str]


# # הגדרת המודל עבור OpenAI
# MODEL = "openai:gpt-4o-mini"

# SYSTEM_PROMPT = (
#     "You are an assistant for a notebook of source documents. "
#     "Always use the available tools to search and inspect documents when answering questions. "
#     "If information is found in active sources, cite the source name in your answer."
# )

# # checkpointer לשמירה על היסטוריית השיחה
# checkpointer = InMemorySaver()


# def _make_tools(store: SourceStore):

#     @tool
#     def search_sources(query: str) -> str:
#         """Find passages in the active sources that are relevant to a query"""
#         docs = store.search(query=query)
#         if not docs:
#             return "No relevant documents found in the active sources"
#         return format_docs(docs)

#     @tool
#     def list_sources() -> str:
#         """List all available source documents in the notebook store"""
#         sources = store.list()
#         if not sources:
#             return "No sources currently loaded in the store"
#         return "\n".join(
#             [f"- {s.name} (ID: {s.id}, Active: {s.active})" for s in sources]
#         )

#     @tool
#     def get_source(source_id: str) -> str:
#         """Get source document content by its ID"""
#         source = store.get(source_id)
#         if not source:
#             return f"Source with ID {source_id} not found"
#         return f"Name: {source.name}\nContent: {source.content}"
   
#     @tool
#     def search_web_and_add_sources(topic: str) -> str:
#         """Search the live web using Firecrawl for a given topic, scrape relevant pages,
#         add them to the store, and return the extracted passages.
#         """
#         added = search_and_index_web(topic)
#         if not added:
#             return f"No new quality web sources found for topic: '{topic}'."

#         # שליפת הקטעים הרלוונטיים
#         docs = store.search(query=topic, k=5)
        
#         if not docs:
#             return (
#                 f"Successfully indexed the following web sources: {', '.join(added)}. "
#                 f"Please use 'list_sources' or general retrieval to inspect them."
#             )

#         return (
#             f"Successfully scraped and indexed web sources ({', '.join(added)}).\n\n"
#             f"Here are the relevant passages:\n{format_docs(docs)}"
#         )

#     return [search_sources, list_sources, get_source, search_web_and_add_sources]

 

# def answer(question: str, thread_id: str) -> Answer:
#     agent = create_agent(
#         model=MODEL,
#         system_prompt=SYSTEM_PROMPT,
#         checkpointer=checkpointer,
#         tools=_make_tools(store),
#     )

#     config = {"configurable": {"thread_id": thread_id}}
#     result = agent.invoke(
#         {"messages": [{"role": "user", "content": question}]}, config=config
#     )

#     last_msg = result["messages"][-1]
#     text = getattr(last_msg, "content", str(last_msg))

#     return Answer(text=text, sources=[])

from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from core.firecrawl_service import search_and_index_web
from core.sources import format_docs
from core.store import SourceStore, store


@dataclass
class Answer:
    text: str
    sources: list[str]


# הגדרת המודל עבור OpenAI
MODEL = "openai:gpt-4o-mini"

# --- כאן מוסיפים את ההנחיה המפורשת ---
SYSTEM_PROMPT = (
    "You are an assistant for a notebook of source documents.\n"
    "Always use the available tools to search and inspect documents when answering questions.\n"
    "When answering, explicitly mention the exact source name (e.g., 'Source: README.md' or 'Source: [filename]') "
    "from which the information was retrieved.\n"
    "Do not invent, hallucinate, or output external URLs (like GitHub links) unless they are explicitly written inside the source text."
)

# checkpointer לשמירה על היסטוריית השיחה
checkpointer = InMemorySaver()


def _make_tools(store: SourceStore):

    @tool
    def search_sources(query: str) -> str:
        """Find passages in the active sources that are relevant to a query"""
        docs = store.search(query=query)
        if not docs:
            return "No relevant documents found in the active sources"
        return format_docs(docs)

    @tool
    def list_sources() -> str:
        """List all available source documents in the notebook store"""
        sources = store.list()
        if not sources:
            return "No sources currently loaded in the store"
        return "\n".join(
            [f"- {s.name} (ID: {s.id}, Active: {s.active})" for s in sources]
        )

    @tool
    def get_source(source_id: str) -> str:
        """Get source document content by its ID"""
        source = store.get(source_id)
        if not source:
            return f"Source with ID {source_id} not found"
        return f"Name: {source.name}\nContent: {source.content}"

    @tool
    def search_web_and_add_sources(topic: str) -> str:
        """Search the live web using Firecrawl for a given topic, scrape relevant pages,
        add them to the store, and return the extracted passages.
        """
        added = search_and_index_web(topic)
        if not added:
            return f"No new quality web sources found for topic: '{topic}'."

        docs = store.search(query=topic, k=5)

        if not docs:
            return (
                f"Successfully indexed the following web sources: {', '.join(added)}. "
                f"Please use 'list_sources' or general retrieval to inspect them."
            )

        return (
            f"Successfully scraped and indexed web sources ({', '.join(added)}).\n\n"
            f"Here are the relevant passages:\n{format_docs(docs)}"
        )

    return [search_sources, list_sources, get_source, search_web_and_add_sources]


def answer(question: str, thread_id: str) -> Answer:
    agent = create_agent(
        model=MODEL,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
        tools=_make_tools(store),
    )

    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]}, config=config
    )

    last_msg = result["messages"][-1]
    text = getattr(last_msg, "content", str(last_msg))

    # חילוץ המקורות שנעשה בהם שימוש מתוך ה-Store Active Sources
    active_sources = [s.name for s in store.list() if getattr(s, "active", True)]

    return Answer(text=text, sources=active_sources)