from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, MessagesState
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from app.agent.prompt import system_message
from app.agent.db import db

load_dotenv()

model = init_chat_model("gemini-2.0-flash", model_provider="google-genai")

toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=system_message),
    MessagesPlaceholder(variable_name="messages")
])

node = create_react_agent(model=model, tools=tools, prompt=prompt)

# ✅ No need to set input schema manually
graph = StateGraph(MessagesState)
graph.add_node("agent", node)
graph.set_entry_point("agent")
graph.set_finish_point("agent")

memory = MemorySaver()


agent_executor = graph.compile(checkpointer=memory)
