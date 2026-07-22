from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import products, categories, stats, support
from .database.database import init_db
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize database
init_db()

app = FastAPI(
    title="Smart Support System API",
    description="AI-powered customer support system with product catalog",
    version="1.0.0"
)

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
app.include_router(support.router, prefix="/api/support", tags=["support"])  # ✅ Uncommented

@app.get("/")
async def root():
    return {"message": "Smart Support System API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}