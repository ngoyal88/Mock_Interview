from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.interview_brain import generate_question

router = APIRouter()

class InterviewStartRequest(BaseModel):
    name: str
    resume: str
    role: str = "SDE-1"
    phase: str = "behavioral"  # optional override

@router.post("/start_interview")
def start_interview(data: InterviewStartRequest):
    try:
        welcome = f"Hello {data.name}, welcome to your AI interview for the {data.role} position."
        question = generate_question(phase=data.phase, resume=data.resume)

        return {
            "welcome": welcome,
            "question": question,
            "phase": data.phase
        }

    except Exception as e:
        print(f"Error in start_interview: {e}")
        raise HTTPException(status_code=500, detail="Failed to start interview.")
