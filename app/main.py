from fastapi import FastAPI
from app.api.routes import router
from app.core.logging import logger
import sys

sys.stdout.reconfigure(encoding='utf-8')

app = FastAPI(
    title="Agentic Honeypot API",
    description="AI-powered scam detection honeypot",
    version="1.0"
)

# Include routes
app.include_router(router)

# Root health check
@app.get("/")
def root():
    return {"status": "running"}

@app.on_event("startup")
async def startup_event():
    logger.info("Honeypot API started")

