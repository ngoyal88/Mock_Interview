from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from parser.affinda_parser import parse_resume
import traceback
from routes import interview
from pydantic import BaseModel
import subprocess
import os

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

@app.post("/run_code")
async def run_code(req: CodeRequest):
    lang = req.language
    code = req.code
    output = ""

    try:
        if lang == "python":
            with open("code.py", "w") as f:
                f.write(code)
            result = subprocess.run(["python", "code.py"], capture_output=True, text=True, timeout=5)
        
        elif lang == "javascript":
            with open("code.js", "w") as f:
                f.write(code)
            result = subprocess.run(["node", "code.js"], capture_output=True, text=True, timeout=5)

        elif lang == "typescript":
            with open("code.ts", "w") as f:
                f.write(code)
            subprocess.run(["tsc", "code.ts"], timeout=5)
            result = subprocess.run(["node", "code.js"], capture_output=True, text=True, timeout=5)

        elif lang == "cpp":
            with open("code.cpp", "w") as f:
                f.write(code)
            subprocess.run(["g++", "code.cpp", "-o", "code.out"], timeout=5)
            result = subprocess.run(["./code.out"], capture_output=True, text=True, timeout=5)

        elif lang == "c":
            with open("code.c", "w") as f:
                f.write(code)
            subprocess.run(["gcc", "code.c", "-o", "code_c.out"], timeout=5)
            result = subprocess.run(["./code_c.out"], capture_output=True, text=True, timeout=5)

        elif lang == "java":
            with open("Main.java", "w") as f:
                f.write(code)
            subprocess.run(["javac", "Main.java"], timeout=5)
            result = subprocess.run(["java", "Main"], capture_output=True, text=True, timeout=5)

        elif lang == "go":
            with open("main.go", "w") as f:
                f.write(code)
            result = subprocess.run(["go", "run", "main.go"], capture_output=True, text=True, timeout=5)

        else:
            return {"output": "❌ Unsupported language."}

        output = result.stdout or result.stderr or "✅ Success. No output."
        return {"output": output}

    except subprocess.TimeoutExpired:
        return {"output": "⏱️ Code execution timed out."}
    except Exception as e:
        return {"output": f"❌ Error: {str(e)}"}
