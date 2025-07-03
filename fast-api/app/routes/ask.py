from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from app.agent.agent import agent_executor

router = APIRouter()

class AgentQuery(BaseModel):
    question: str

@router.post("/ask")
async def ask_agent(query: AgentQuery):
    async def event_generator():
        inputs = {
            "messages": [HumanMessage(content=query.question)],
        }
        config = {"configurable": {"thread_id": "session-1"}}

        async for step in agent_executor.astream(inputs, config, stream_mode="values"):
            message = step["messages"][-1]
            if isinstance(message, AIMessage):
                yield message.content + "\n"

    return StreamingResponse(event_generator(), media_type="text/plain")
