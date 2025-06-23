# The FastAPI entry point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import game_router, auth_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(game_router, prefix="/game")

@app.get("/ping")
def ping():
    return {"message": "pong"}