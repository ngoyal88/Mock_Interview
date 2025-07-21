from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.resume_parser import parse_resume
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
@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse resume using OpenResume parser
    Now completely free with no API dependencies!
    """
    try:
        print(f"📄 Received file: {file.filename}")
        print(f"📊 File size: {file.size} bytes" if hasattr(file, 'size') else "")
        print(f"📋 Content type: {file.content_type}")
        
        # Read file bytes
        file_bytes = await file.read()
        
        # Validate file
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file received")
        
        # Parse using OpenResume parser (completely free!)
        parsed_data = parse_resume(file_bytes, file.filename)
        
        # Log success
        candidate_name = parsed_data.get("data", {}).get("name", {}).get("raw", "Unknown")
        skills_count = len(parsed_data.get("data", {}).get("skills", []))
        experience_count = len(parsed_data.get("data", {}).get("workExperience", []))
        
        print(f"✅ Successfully parsed resume for: {candidate_name}")
        print(f"🎯 Extracted {skills_count} skills and {experience_count} work experiences")
        
        return {
            "success": True,
            "parsed_data": parsed_data,
            "summary": {
                "candidate_name": candidate_name,
                "skills_found": skills_count,
                "experience_count": experience_count,
                "parser_used": "OpenResume (Free)"
            }
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️ Resume parsing error: {error_msg}")
        traceback.print_exc()
        
        # Return detailed error for debugging
        raise HTTPException(
            status_code=500, 
            detail={
                "error": error_msg,
                "file_info": {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "file_size": len(file_bytes) if 'file_bytes' in locals() else 0
                },
                "parser": "OpenResume"
            }
        )

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