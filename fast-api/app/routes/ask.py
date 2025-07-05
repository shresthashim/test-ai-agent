from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from app.agent import agent_executor

router = APIRouter()

class AgentQuery(BaseModel):
    question: str
    thread_id: str = "session-1"

class AgentResponse(BaseModel):
    response: str

@router.post("/ask", response_model=AgentResponse, tags=["Agent"])
async def ask_agent(query: AgentQuery):
    if not query.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    inputs = {
        "messages": [HumanMessage(content=query.question)],
    }
    config = {"configurable": {"thread_id": query.thread_id}}

    full_response = []

    try:
        for step in agent_executor.stream(inputs, config, stream_mode="values"):
            message = step["messages"][-1]
            if isinstance(message, AIMessage):
                full_response.append(message.content)

        combined_response = "".join(full_response)
        return {"response": combined_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
