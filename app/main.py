# The FastAPI entry point

from fastapi import FastAPI 
from app.routes import router 

app = FastAPI(title="Diplomacy API")
app.include_router(router)