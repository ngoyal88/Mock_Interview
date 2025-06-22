from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from parser.affinda_parser import parse_resume
import traceback
from routes import interview

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
