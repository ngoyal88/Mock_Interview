from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm_chain import build_chain
from services.prompt_templates import start_prompt, followup_prompt

router = APIRouter()

# -------------------------------
# Endpoint: /start_interview
# -------------------------------

class StartInterviewRequest(BaseModel):
    name: str
    resume: str
    role: str = "SDE-1"

class StartInterviewResponse(BaseModel):
    question: str

@router.post("/start_interview", response_model=StartInterviewResponse)
async def start_interview(data: StartInterviewRequest):
    """
    Generate the first smart interview question using LangChain + local LLM.
    """
    try:
        chain = build_chain(start_prompt)
        result = chain.invoke({
            "name": data.name,
            "resume": data.resume,
            "role": data.role
        })
        return {"question": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------
# Endpoint: /interview/respond
# -------------------------------

class FollowUpRequest(BaseModel):
    name: str
    resume: str
    last_question: str
    user_answer: str
    role: str = "SDE-1"

class FollowUpResponse(BaseModel):
    follow_up_question: str

@router.post("/interview/respond", response_model=FollowUpResponse)
async def interview_respond(data: FollowUpRequest):
    """
    Accepts the user's Hinglish or English answer and generates the next question.
    """
    try:
        chain = build_chain(followup_prompt)
        result = chain.invoke({
            "name": data.name,
            "resume": data.resume,
            "last_question": data.last_question,
            "user_answer": data.user_answer,
            "role": data.role
        })
        return {"follow_up_question": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
