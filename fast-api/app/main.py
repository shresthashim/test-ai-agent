from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ask import router as ask_router
from app.db import Base, engine
import app.models
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables in real estate DB
Base.metadata.create_all(bind=engine)

app.include_router(ask_router, prefix="/api/agent")
