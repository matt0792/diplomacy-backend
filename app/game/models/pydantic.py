# Pydantic models for req / res 

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict

# === Request Models === 

class CreateGameRequest(BaseModel):
    rules: Optional[List[str]] = None
    game_name: str
    creator_id: str
    
class RegisterPlayerRequest(BaseModel):
    game_id: str
    player_id: str
    player_name: str
    power: Optional[str] = None
    
class SubmitOrdersRequest(BaseModel):
    player_id: str
    orders: List[str]
    
class GetOrdersRequest(BaseModel):
    game_id: str
    
class GetValidOrdersRequest(BaseModel):
    game_id: str
    power: str
    
class GenericRequest(BaseModel):
    game_id: str
    
# === Response Models === 

class SuccessResponse(BaseModel): 
    message: Optional[str]
    data: Optional[Dict] = None
    
class GameStateResponse(BaseModel):
    game_id: str
    state: Dict
    
class GameRender(BaseModel):
    game_id: str
    svg: str
    
class CreateGameResponse(BaseModel):
    message: str
    game_id: str
    game_name: str
    creator_id: str
    
class PlayerInfo(BaseModel):
    power: str
    name: str
    
class GameSummaryResponse(BaseModel):
    game_id: str
    players: Dict[str, PlayerInfo]
    game_name: str
    creator_id: str