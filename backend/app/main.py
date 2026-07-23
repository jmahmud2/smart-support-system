from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routes import products, categories, stats, support
from .database.database import init_db
from .utils.logger import get_logger, log_request, log_response
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Initialize logger
logger = get_logger(__name__)

# Initialize database
init_db()
logger.info("Database initialized")

app = FastAPI(
    title="Smart Support System API",
    description="AI-powered customer support system with product catalog",
    version="1.0.0"
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    log_request(logger, request.method, request.url.path)
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = time.time() - start_time
    log_response(logger, response.status_code, duration)
    
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(support.router, prefix="/api/support", tags=["support"])

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Smart Support System API", "version": "1.0.0"}

@app.get("/health")
async def health():
    logger.info("Health check")
    return {"status": "healthy"}

logger.info("Application startup complete")