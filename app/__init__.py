from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

# FastAPI app setup
app = FastAPI()

# CORS settings
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
