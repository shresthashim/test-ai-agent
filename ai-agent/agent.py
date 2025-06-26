import os
import re
import json
from dotenv import load_dotenv
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List

# --- Data ---

DUMMY_LISTINGS = [
    {"id": 1, "location": "downtown", "price": 950, "bedrooms": 2},
    {"id": 2, "location": "suburbs", "price": 850, "bedrooms": 2},
    {"id": 3, "location": "downtown", "price": 1200, "bedrooms": 3},
    {"id": 4, "location": "downtown", "price": 999, "bedrooms": 1},
]

# --- Environment Setup ---

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the Gemini model
llm = genai.GenerativeModel("gemini-2.0-flash")

# --- Types ---

class AgentState(TypedDict):
    user_input: str
    filters: Optional[dict]
    matches: Optional[List[dict]]
    response: Optional[str]
    clarify_needed: Optional[bool]

# --- Functions ---

def parse_query(state: AgentState) -> AgentState:
    user_input = state["user_input"]
    prompt = (
        "Extract the property filters from the message below and return them as a JSON like:\n"
        '{ "location": ..., "bedrooms": ..., "price": ... }\n\n'
        f"Message: {user_input}"
    )

    response = llm.generate_content(prompt)
    raw_text = response.text.strip()

    try:
        # Extract the first valid JSON object from the text (even if Gemini adds extra text)
        json_str = re.search(r'\{.*\}', raw_text, re.DOTALL).group()
        filters = json.loads(json_str)
    except Exception:
        return {"clarify_needed": True, "user_input": user_input}

    return {"filters": filters, "user_input": user_input}

def search_properties(state: AgentState) -> AgentState:
    filters = state["filters"]
    print("🔍 Extracted Filters:", filters)

    location = filters.get("location", "").lower()

    # Convert bedrooms to int safely
    try:
        bedrooms = int(filters.get("bedrooms"))
    except Exception:
        bedrooms = None

    # Parse price filter safely
    price_str = str(filters.get("price"))
    try:
        if "<" in price_str:
            price = int(price_str.replace("<", "").strip())
        else:
            price = int(price_str.strip())
    except Exception:
        price = 99999  # fallback to very high price

    matches = []
    for prop in DUMMY_LISTINGS:
        if (
            prop["location"].lower() == location and
            prop["bedrooms"] == bedrooms and
            prop["price"] <= price
        ):
            matches.append(prop)

    return {**state, "matches": matches}

def suggest_properties(state: AgentState) -> AgentState:
    matches = state.get("matches", [])
    if not matches:
        return {"response": "Sorry, we couldn't find any matching properties."}

    listing_text = "\n".join(
        f"ID {p['id']}: {p['bedrooms']}BR in {p['location']} for ${p['price']}" for p in matches
    )

    prompt = f"Summarize these property listings in a friendly tone:\n{listing_text}"

    response = llm.generate_content(prompt)
    return {"response": response.text}

def clarify_query(state: AgentState) -> AgentState:
    return {
        "response": "I couldn’t understand your request. Could you please specify location, number of bedrooms, and budget?"
    }

# --- State Graph Setup ---

builder = StateGraph(AgentState)  # type: ignore

builder.add_node("parse", parse_query)
builder.add_node("search", search_properties)
builder.add_node("suggest", suggest_properties)
builder.add_node("clarify", clarify_query)

builder.set_entry_point("parse")

# Conditional edge: if parsing fails -> clarify, else -> search
builder.add_conditional_edges(
    "parse",
    lambda state: "clarify" if state.get("clarify_needed") else "search"
)

builder.add_edge("search", "suggest")
builder.add_edge("suggest", END)
builder.add_edge("clarify", END)

graph = builder.compile()

# --- Run Example ---

result = graph.invoke({
    "user_input": "I'm looking for a 2-bedrooms apartment in downtown under $1000"
})

print(result["response"])
