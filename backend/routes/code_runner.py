# backend/routes/code_runner.py

from fastapi import APIRouter
from pydantic import BaseModel
import requests
from datetime import datetime
from firebase_admin import firestore

router = APIRouter()
db = firestore.client()

JUDGE0_API_URL = "https://ce.judge0.com/submissions/?base64_encoded=false&wait=true"

class CodeRequest(BaseModel):
    language_id: int
    source_code: str
    stdin: str = ""
    expected_output: str = ""
    userId: str | None = None
    question: str | None = None

@router.post("/run_code")
async def run_code(req: CodeRequest):
    payload = {
        "language_id": req.language_id,
        "source_code": req.source_code,
        "stdin": req.stdin,
        "expected_output": req.expected_output
    }

    try:
        response = requests.post(JUDGE0_API_URL, json=payload)
        result = response.json()

        if req.userId:
            db.collection("users").document(req.userId).collection("submissions").add({
                "language_id": req.language_id,
                "question": req.question or "",
                "code": req.source_code,
                "output": result.get("stdout", "") or result.get("stderr", ""),
                "status": result.get("status", {}).get("description", "Unknown"),
                "success": result.get("status", {}).get("id", 0) == 3,
                "timestamp": datetime.utcnow()
            })

        return result

    except Exception as e:
        return {"output": f"❌ Error: {str(e)}"}
