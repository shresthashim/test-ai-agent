from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from app.agent.prompt import system_message
from app.agent.db import db

# Load environment variables
load_dotenv()

# Initialize the model
model = init_chat_model("gemini-2.0-flash", model_provider="google-genai")



# Set up tools
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()


node = create_react_agent(model, tools, prompt=system_message)


# Build LangGraph workflow
graph = StateGraph(state_schema=MessagesState)
graph.add_node("agent", node)
graph.set_entry_point("agent")
graph.set_finish_point("agent")

# BUG (when using memory) : ValueError: Checkpointer requires one or more of the following 'configurable' keys: []
# memory = MemorySaver()
# # Compile the graph with checkpointing
# agent_executor = graph.compile(checkpointer=memory)


agent_executor = graph.compile()
