from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from parser.affinda_parser import parse_resume
import traceback
from routes import interview
from pydantic import BaseModel
import subprocess
import os
import subprocess, tempfile, os
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(interview.router)

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        print(f"Received file: {file.filename}")
        file_bytes = await file.read()
        parsed_data = parse_resume(file_bytes, file.filename)
        return {"parsed_data": parsed_data}
    except Exception as e:
        print("⚠️ Error:", str(e))
        traceback.print_exc()  # NEW: prints detailed stack trace
        raise HTTPException(status_code=500, detail=str(e))


class CodeRequest(BaseModel):
    language: str
    code: str
    question: str | None = None
    userId: str | None = None

@app.post("/run_code")
async def run_code(req: CodeRequest):
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            lang = req.language.lower()
            file_map = {
                "python": ("code.py", ["python", "code.py"]),
                "javascript": ("code.js", ["node", "code.js"]),
                "java": ("Main.java", ["javac", "Main.java", "&&", "java", "Main"]),
                "cpp": ("code.cpp", ["g++", "code.cpp", "-o", "a.out", "&&", "./a.out"]),
                "c": ("code.c", ["gcc", "code.c", "-o", "a.out", "&&", "./a.out"]),
                "go": ("main.go", ["go", "run", "main.go"]),
            }

            if lang not in file_map:
                return {"output": "❌ Unsupported language."}

            filename, cmd = file_map[lang]
            with open(filename, "w") as f:
                f.write(req.code)

            result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True, timeout=5)

            output = result.stdout or result.stderr or "✅ No output"
            success = result.returncode == 0

            if req.userId:
                db.collection("users").document(req.userId).collection("submissions").add({
                    "language": req.language,
                    "question": req.question,
                    "code": req.code,
                    "output": output,
                    "success": success,
                    "timestamp": datetime.now(datetime.timezone.utc)
                })

            return {"output": output}

    except subprocess.TimeoutExpired:
        return {"output": "⏱ Code execution timed out."}
    except Exception as e:
        return {"output": f"❌ Error: {str(e)}"}