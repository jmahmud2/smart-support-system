from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routes import products, categories, stats, support, auth
from .database.database import init_db
from .utils.logger import get_logger, log_request, log_response
from .utils.error_handler import handle_exception
from .config import Config
import os
import time
import uuid
from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)

init_db()
logger.info("Database initialized")

app = FastAPI(
    title=Config.API_TITLE,
    description="AI-powered customer support system with product catalog",
    version=Config.API_VERSION
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return handle_exception(exc, request)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    log_request(logger, request.method, request.url.path, {"request_id": request_id})
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        log_response(logger, response.status_code, duration, {"request_id": request_id})
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Request {request_id} failed after {duration:.2f}s: {e}")
        raise

# CORS middleware - future-proof with regex for Vercel previews
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_origin_regex=Config.ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(support.router, prefix="/api/support", tags=["support"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Smart Support System API", "version": Config.API_VERSION}

@app.get("/health")
async def health():
    return {"status": "healthy"}

logger.info("Application startup complete")