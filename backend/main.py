import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.db import init_db
from backend.router import router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Futuristic AI-powered Drone Delivery Command Center Backend",
    version="1.0.0"
)

# Set up CORS middleware to allow cross-origin requests from React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initializes tables on startup if PostgreSQL is connected."""
    try:
        await init_db()
        print(">>> Database initialized successfully.")
    except Exception as e:
        print(">>> WARNING: Could not connect to PostgreSQL. Tables will not be auto-created.")
        print(f">>> Details: {e}")
        print(">>> System running in dynamic simulation mode with database fallbacks enabled.")

# Register routes under the prefix '/api'
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "message": "AeroCom AI Command Center active. Telemetry streams ready."
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
