from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import traceback
"""from routes import interview, code_runner,tts"""
from routes import resume
from redis.asyncio import Redis
from firebase_config import db
from config import get_settings
from utils.logger import setup_logging, get_logger

# initialise logging BEFORE anything else
setup_logging()
log = get_logger(__name__)
settings = get_settings()

app = FastAPI(title="AI-Interviewer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router)
"""
app.include_router(interview.router)
app.include_router(health.router)
app.include_router(code_runner.router)
"""


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "resume_parser": "OpenResume (Free)",
        "features": ["PDF parsing", "DOCX parsing", "Skills extraction", "Experience extraction"]
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Mock Interview Backend",
        "resume_parser": "OpenResume - Free & Open Source",
        "endpoints": {
            "upload_resume": "/upload_resume",
            "health": "/health",
            "docs": "/docs"
        },
        "features": [
            "Free resume parsing (no API costs)",
            "AI-powered interviews",
            "Code execution",
            "Text-to-speech"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

""" 
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
"""