from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from app.agent.agent import agent_executor

router = APIRouter()

class AgentQuery(BaseModel):
    question: str

@router.post("/chat")
async def start_chat(query: AgentQuery):
    async def event_generator():
        inputs = {
            "messages": [HumanMessage(content=query.question)],
            "configurable": {"thread_id": "session-1"}
        }
        async for step in agent_executor.astream(inputs, stream_mode="values"):
            message = step["messages"][-1]
            if isinstance(message, AIMessage):
                yield message.content + "\n"
    return StreamingResponse(event_generator(), media_type="text/plain")

@router.post("/chat/{thread_id}")
async def continue_chat(thread_id: str, query: AgentQuery):
    async def event_generator():
        inputs = {
            "messages": [HumanMessage(content=query.question)],
            "configurable": {"thread_id": thread_id}
        }
        async for step in agent_executor.astream(inputs, stream_mode="values"):
            message = step["messages"][-1]
            if isinstance(message, AIMessage):
                yield message.content + "\n"
    return StreamingResponse(event_generator(), media_type="text/plain")
