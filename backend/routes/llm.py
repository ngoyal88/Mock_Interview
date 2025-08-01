"""
Simple route to verify Grok credentials.
"""
from fastapi import APIRouter, HTTPException
from services.grok_service import GrokService

router = APIRouter(prefix="/llm", tags=["LLM"])
grok = GrokService()


@router.get("/ping")
async def ping():
    """Returns 'pong' if Grok key works."""
    reply = await grok.chat([{"role": "user", "content": "Respond with: pong"}])
    if "pong" in reply.lower():
        return {"status": "ok", "reply": reply}
    raise HTTPException(502, "Grok API unreachable or invalid key")
