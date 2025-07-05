import os
from dotenv import load_dotenv
import psycopg
from psycopg import Connection
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import create_react_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from app.prompt import system_message
from app.db import langchain_db  # SQLDatabase from real estate DB

load_dotenv()

CHECKPOINT_DB_NAME = os.getenv("POSTGRES_DB_CHECKPOINT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

# Build full checkpoint URI for psycopg connection
CHECKPOINT_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{CHECKPOINT_DB_NAME}"


if not CHECKPOINT_URI:
    raise RuntimeError("Checkpoint DB URI not set in .env")

# Init LLM model (Gemini)
model = init_chat_model("gemini-2.0-flash", model_provider="google-genai")

# Setup SQLDatabaseToolkit with your real estate DB
toolkit = SQLDatabaseToolkit(db=langchain_db, llm=model)
tools = toolkit.get_tools()

# Setup prompt template with system message + messages placeholder
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=system_message),
    MessagesPlaceholder(variable_name="messages")
])

# Create LangGraph react agent node
agent_node = create_react_agent(model=model, tools=tools, prompt=prompt)

# Setup LangGraph state graph with messages state
graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.set_entry_point("agent")
graph.set_finish_point("agent")

# Connect to checkpoint DB with psycopg (for saving graph state)
conn_kwargs = {"autocommit": True}
conn: Connection = psycopg.connect(CHECKPOINT_URI, **conn_kwargs)

# Setup checkpoint saver
checkpointer = PostgresSaver(conn)
checkpointer.setup()

# Compile graph into an executable agent
agent_executor = graph.compile(checkpointer=checkpointer)
