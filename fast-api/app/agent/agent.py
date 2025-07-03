# agent.py
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from psycopg import Connection
import psycopg
import os

from app.agent.prompt import system_message
from app.agent.db import db

load_dotenv()

# Set up model and toolkit
model = init_chat_model("gemini-2.0-flash", model_provider="google-genai")
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=system_message),
    MessagesPlaceholder(variable_name="messages")
])
node = create_react_agent(model=model, tools=tools, prompt=prompt)

# Build the graph
graph = StateGraph(MessagesState)
graph.add_node("agent", node)
graph.set_entry_point("agent")
graph.set_finish_point("agent")

# ✅ Set up PostgresSaver
DB_URI = os.getenv("POSTGRES_URI", "postgresql://ashim:yourpassword@localhost:5432/langgraph_memory")
conn_kwargs = {"autocommit": True}
pool = psycopg.Connection.connect(DB_URI, **conn_kwargs)
checkpointer = PostgresSaver(pool)
checkpointer.setup()  # first-time setup: creates required tables :contentReference[oaicite:1]{index=1}

# Compile graph with persistent memory
agent_executor = graph.compile(checkpointer=checkpointer)
