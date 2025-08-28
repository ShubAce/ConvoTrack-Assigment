from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from qa_agent_ai import AdvancedCaseStudyQAAgent
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uvicorn

# Initialize the FastAPI application
app = FastAPI(
    title="ConvoTrack QA Agent API",
    description="Autonomous Business Intelligence API for ConvoTrack Case Studies",
    version="2.0.0"
)

# Configure CORS to allow requests from the frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for API Data Validation ---

class QuestionRequest(BaseModel):
    """The request model for an incoming user question."""
    question: str
    # No longer needs analysis_type, as the agent is autonomous

class QuestionResponse(BaseModel):
    """The response model for an AI-generated answer."""
    question: str
    answer: str
    sources: List[Dict[str, Any]]  # Expects a list of rich source objects
    agent_type: str
    confidence: str
    analysis_type: Optional[str] = None # The type the AI chose

class HealthResponse(BaseModel):
    """The response model for the health check endpoint."""
    status: str
    message: str
    agent_initialized: bool

# --- Global Variables ---

qa_agent: Optional[AdvancedCaseStudyQAAgent] = None
# Use a thread pool to run the synchronous AI agent code without blocking the async API
executor = ThreadPoolExecutor(max_workers=3)

# --- FastAPI Events ---

@app.on_event("startup")
async def startup_event():
    """
    Initializes the AdvancedCaseStudyQAAgent when the API server starts.
    This is a long-running operation, so it's done once on startup.
    """
    global qa_agent
    try:
        print("🚀 Initializing ConvoTrack QA Agent...")
        # Path to the scraped articles that form the knowledge base
        scraped_path = "../extractContent/scraped_articles_selenium"
        qa_agent = AdvancedCaseStudyQAAgent(scraped_path)
        print("✅ QA Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize QA Agent: {e}")
        qa_agent = None

# --- API Endpoints ---

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Provides a health check of the API and the AI agent's status."""
    if qa_agent is None:
        raise HTTPException(status_code=503, detail="QA Agent is not initialized or failed to load.")
    
    return HealthResponse(
        status="healthy",
        message="ConvoTrack QA Agent API is running and agent is initialized.",
        agent_initialized=True
    )

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    The primary endpoint to process a user's business question.
    It now relies on the agent's autonomous routing.
    """
    if qa_agent is None:
        raise HTTPException(status_code=503, detail="QA Agent not initialized. Please check server logs.")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        print(f"🔍 Processing question: '{request.question[:100]}...'")
        loop = asyncio.get_event_loop()
        
        # Run the synchronous qa_agent.ask method in the thread pool executor
        response = await loop.run_in_executor(
            executor, 
            qa_agent.ask, 
            request.question
        )
        
        print(f"✅ Successfully processed question. AI chose '{response.get('analysis_type')}' analysis.")
        return QuestionResponse(**response)
    
    except Exception as e:
        import traceback
        print(f"❌ Error processing question: {str(e)}")
        print(f"📋 Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"An internal error occurred while processing the question."
        )

# --- Server Execution ---

if __name__ == "__main__":
    print("🚀 Starting ConvoTrack QA Agent API Server...")
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
