from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from qa_agent_ai import AdvancedCaseStudyQAAgent
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="ConvoTrack QA Agent API",
    description="Advanced Business Intelligence API for ConvoTrack Case Studies",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class QuestionRequest(BaseModel):
    question: str
    analysis_type: Optional[str] = "default"

# 1. Create a new model to represent a single source object
class Source(BaseModel):
    content: str
    url: str
    article_number: str
    relevance: str
    relevance_score: Optional[int] = None
    content_length: Optional[int] = None


# 2. Update QuestionResponse to use a list of the new Source model
class QuestionResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source] # <--- THE FIX IS HERE
    agent_type: str
    confidence: str
    analysis_type: str

# You might also want a model for the incoming request
class QuestionRequest(BaseModel):
    question: str
    analysis_type: str = "default"

class TopicsResponse(BaseModel):
    topics: List[str]

class HealthResponse(BaseModel):
    status: str
    message: str
    agent_initialized: bool

class ConversationInsightsResponse(BaseModel):
    insights: Dict[str, Any]

# Global QA agent instance
qa_agent = None
executor = ThreadPoolExecutor(max_workers=3)

@app.on_event("startup")
async def startup_event():
    """Initialize QA agent on startup"""
    global qa_agent
    try:
        print("🚀 Initializing ConvoTrack QA Agent...")
        scraped_path = "../extractContent/scraped_articles_selenium"
        qa_agent = AdvancedCaseStudyQAAgent(scraped_path)
        print("✅ QA Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize QA Agent: {e}")
        qa_agent = None

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="ConvoTrack QA Agent API is running",
        agent_initialized=qa_agent is not None
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    if qa_agent is None:
        raise HTTPException(status_code=503, detail="QA Agent not initialized")
    
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        agent_initialized=True
    )

def run_qa_query(question: str, analysis_type: str = "default") -> Dict[str, Any]:
    """Run QA query in thread"""
    try:
        print(f"🧠 QA Agent processing: {question[:50]}... (type: {analysis_type})")
        
        if analysis_type != "default":
            result = qa_agent.ask_with_analysis_type(question, analysis_type)
        else:
            result = qa_agent.ask(question)
        
        print(f"🎯 QA processing complete. Result keys: {list(result.keys())}")
        return result
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"💥 QA Agent error: {str(e)}")
        print(f"📋 QA Traceback:\n{error_traceback}")
        
        # Return error in the expected format
        return {
            "question": question,
            "answer": f"I encountered an error while processing your question: {str(e)}",
            "sources": [],
            "agent_type": "error_response",
            "confidence": "low",
            "error": str(e),
            "analysis_type": analysis_type
        }

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Process a business question"""
    if qa_agent is None:
        raise HTTPException(status_code=503, detail="QA Agent not initialized")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        print(f"🔍 Processing question: {request.question[:100]}...")
        print(f"📊 Analysis type: {request.analysis_type}")
        
        # Run QA query in executor to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            executor, 
            run_qa_query, 
            request.question, 
            request.analysis_type
        )
        
        print(f"✅ Successfully processed question")
        print(f"📝 Response keys: {list(response.keys())}")
        
        return QuestionResponse(**response)
    
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"❌ Error processing question: {str(e)}")
        print(f"📋 Full traceback:\n{error_traceback}")
        
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing question: {str(e)}\n\nTraceback:\n{error_traceback}"
        )

@app.get("/topics", response_model=TopicsResponse)
async def get_case_study_topics():
    """Get available case study topics"""
    if qa_agent is None:
        raise HTTPException(status_code=503, detail="QA Agent not initialized")
    
    try:
        topics = qa_agent.get_case_study_topics()
        return TopicsResponse(topics=topics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting topics: {str(e)}")

@app.get("/insights", response_model=ConversationInsightsResponse)
async def get_conversation_insights():
    """Get conversation analytics and insights"""
    if qa_agent is None:
        raise HTTPException(status_code=503, detail="QA Agent not initialized")
    
    try:
        insights = qa_agent.get_conversation_insights()
        return ConversationInsightsResponse(insights=insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting insights: {str(e)}")

@app.post("/search")
async def search_similar_content(request: QuestionRequest):
    """Search for similar content"""
    if qa_agent is None:
        raise HTTPException(status_code=503, detail="QA Agent not initialized")
    
    try:
        loop = asyncio.get_event_loop()
        docs = await loop.run_in_executor(
            executor,
            qa_agent.search_similar_content,
            request.question,
            5
        )
        
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                "metadata": doc.metadata
            })
        
        return {"query": request.question, "results": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching content: {str(e)}")

@app.get("/analysis-types")
async def get_analysis_types():
    """Get available analysis types"""
    return {
        "analysis_types": [
            {
                "id": "default",
                "name": "General Business Analysis",
                "description": "Comprehensive analysis with insights and recommendations",
                "icon": "💼"
            },
            {
                "id": "strategic",
                "name": "Strategic Analysis",
                "description": "Long-term strategic planning and positioning insights",
                "icon": "🎯"
            },
            {
                "id": "trends",
                "name": "Trend Analysis",
                "description": "Market trends and future outlook analysis",
                "icon": "📈"
            },
            {
                "id": "comparative",
                "name": "Comparative Analysis",
                "description": "Side-by-side comparison with benchmarks",
                "icon": "📊"
            },
            {
                "id": "executive",
                "name": "Executive Summary",
                "description": "C-level decision making insights",
                "icon": "📋"
            }
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting ConvoTrack QA Agent API Server...")
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
