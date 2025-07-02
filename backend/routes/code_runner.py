# routes/code_runner.py

from fastapi import APIRouter
from pydantic import BaseModel
import requests
from datetime import datetime
from firebase_config import db
import os
import dotenv

router = APIRouter()

JUDGE0_API_URL = "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

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

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(JUDGE0_API_URL, json=payload, headers=headers)
        print("Judge0 Response:", response.status_code, response.text)

        if not response.ok:
            return {"output": f"❌ Judge0 API error: {response.status_code} - {response.text}"}

        result = response.json()

        if req.userId:
            db.collection("users").document(req.userId).collection("submissions").add({
                "language_id": req.language_id,
                "question": req.question or "",
                "code": req.source_code,
                "output": result.get("stdout", "") or result.get("stderr", ""),
                "status": result.get("status", {}).get("description", "Unknown"),
                "success": result.get("status", {}).get("id", 0) == 3,
                "timestamp": datetime.now(datetime.timezone.utc)
            })

        return result

    except Exception as e:
        return {"output": f"❌ Error: {str(e)}"}
