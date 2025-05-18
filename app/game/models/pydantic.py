# Pydantic models for req / res 

from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# === Request Models === 

class CreateGameRequest(BaseModel):
    game_id: str
    rules: Optional[List[str]] = None
    
class RegisterPlayerRequest(BaseModel):
    game_id: str
    player_id: str
    power: Optional[str] = None
    
class SubmitOrdersRequest(BaseModel):
    game_id: str
    player_id: str
    orders: List[str]
    
class ResolvePhaseRequest(BaseModel):
    game_id: str
    
# === Response Models === 

class SuccessResponse(BaseModel): 
    message: str
    
class GameStateResponse(BaseModel):
    game_id: str
    state: Dict
    
class GameRender(BaseModel):
    game_id: str
    svg: str