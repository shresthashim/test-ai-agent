from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import create_react_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from app.agent.db import tools

# Initialize Gemini 2.0 Flash model from Google GenAI provider
model = init_chat_model("gemini-2.0-flash", model_provider="google-genai")

system_message = """
You are a helpful real estate AI assistant. Use the real_estate_lookup tool
to answer user questions about properties in the database.
"""

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=system_message),
    MessagesPlaceholder(variable_name="messages"),
])

# Create the LangGraph React Agent with Gemini and your tools
node = create_react_agent(model=model, tools=tools, prompt=prompt)

graph = StateGraph(state_schema=MessagesState)
graph.add_node("agent", node)
graph.set_entry_point("agent")
graph.set_finish_point("agent")

agent_executor = graph.compile()
