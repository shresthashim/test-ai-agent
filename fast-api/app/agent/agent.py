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
from app.agent.prompt import system_message
from app.agent.db import db


load_dotenv()


DB_URI = os.getenv("POSTGRES_URI")
if not DB_URI:
    raise RuntimeError("POSTGRES_URI is not set in .env")


model = init_chat_model("gemini-2.0-flash", model_provider="google-genai")


toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()


prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=system_message),
    MessagesPlaceholder(variable_name="messages")
])


agent_node = create_react_agent(model=model, tools=tools, prompt=prompt)


graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.set_entry_point("agent")
graph.set_finish_point("agent")

conn_kwargs = {"autocommit": True}
conn: Connection = psycopg.connect(DB_URI, **conn_kwargs)


checkpointer = PostgresSaver(conn)
checkpointer.setup()  


agent_executor = graph.compile(checkpointer=checkpointer)
