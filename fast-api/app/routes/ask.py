from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.agent.agent import agent_executor
from langchain_core.messages import AIMessage

router = APIRouter()

class AgentQuery(BaseModel):
    question: str

@router.post("/ask")
async def ask_agent(query: AgentQuery):
    async def event_generator():
        inputs = {
            "messages": [HumanMessage(content=query.question)],
            "configurable": {
                "run_id": "test-stream-1"
            }
        }
        async for step in agent_executor.astream(inputs, stream_mode="values"):
            message = step["messages"][-1]
            if isinstance(message, AIMessage):
                yield message.content + "\n"

    return StreamingResponse(event_generator(), media_type="text/plain")


# Find 3-bedroom houses under $300,000 in Texas.