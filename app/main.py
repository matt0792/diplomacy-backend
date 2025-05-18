# The FastAPI entry point

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from app.game.models.pydantic import (
    CreateGameRequest,
    RegisterPlayerRequest,
    SubmitOrdersRequest,
    ResolvePhaseRequest,
    GameStateResponse,
    SuccessResponse,
    GameRender,
)
from app.game.game_manager import GameManager
from app.game.automation import GameAutomation
import os

app = FastAPI()
manager = GameManager()
automation = GameAutomation(manager)

# Create a game
@app.post("/games", response_model=SuccessResponse)
def create_game(req: CreateGameRequest):
    try:
        manager.create_game(game_id=req.game_id, rules=req.rules)
        return SuccessResponse(message=f"Game '{req.game_id}' created.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Register a player
@app.post("/games/{game_id}/register", response_model=SuccessResponse)
def register_player(req: RegisterPlayerRequest):
    try:
        manager.register_player(req.game_id, req.player_id, req.power)
        return SuccessResponse(message=f"Player '{req.player_id}' registered for game '{req.game_id}'.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Start a game
@app.post("/games/{game_id}/start", response_model=SuccessResponse)
def start_game(game_id: str):
    result = manager.start_game(game_id)
    if result["success"]:
        automation.start_automation(game_id)
    return result
    
# Stop a game
@app.post("/games/{game_id}/stop", response_model=SuccessResponse)
def stop_game(game_id: str):
    if game_id not in automation.running_games:
        raise HTTPException(status_code=400, detail="Automation not running for this game.")
    automation.stop_automation(game_id)
    return SuccessResponse(message=f"Game '{game_id}' automation stopped.")

# Submit orders for a power 
@app.post("/games/{game_id}/orders", response_model=SuccessResponse)
def submit_orders(req: SubmitOrdersRequest):
    try:
        manager.submit_orders(req.game_id, req.player_id, req.orders)
        return SuccessResponse(message="Orders submitted successfully.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Resolve a game phase (will probs be removed)
@app.post("/games/{game_id}/resolve", response_model=SuccessResponse)
def resolve_phase(req: ResolvePhaseRequest):
    try:
        manager.resolve_game_phase(req.game_id)
        return SuccessResponse(message=f"Phase resolved for game '{req.game_id}'.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Get game state 
@app.get("/games/{game_id}/state", response_model=GameStateResponse)
def get_game_state(game_id: str):
    try:
        state = manager.get_game_state(game_id)
        return GameStateResponse(game_id=game_id, state=state)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
# Render game to SVG
@app.get("/games/{game_id}/render", response_model=GameRender)
async def render_game_svg(game_id: str):
    try:
        manager.render_game(game_id)

        svg_path = manager.render_game(game_id)

        if not os.path.exists(svg_path):
            raise HTTPException(status_code=500, detail="SVG not found after rendering")

        with open(svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()

        return GameRender(game_id=game_id, svg=svg_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))