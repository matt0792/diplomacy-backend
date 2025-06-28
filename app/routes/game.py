# These are the actual endpoints that the frontend hits for game logic, auth is separate

from typing import List
from fastapi import APIRouter, HTTPException, Query, Path
from app.game.models.pydantic import (
    CreateGameRequest,
    RegisterPlayerRequest,
    SubmitOrdersRequest,
    GameStateResponse,
    SuccessResponse,
    GameRender,
    CreateGameResponse,
    GameSummaryResponse,
    GetOrdersRequest,
    GetValidOrdersRequest,
)
from app.game.game_manager import GameManager
from app.game.automation import GameAutomation
import os
from uuid import uuid4

router = APIRouter(tags=["game"])
manager = GameManager()
automation = GameAutomation(manager)

@router.post("/create", response_model=CreateGameResponse)
def create_game(req: CreateGameRequest):
    game_id = str(uuid4())
    try:
        manager.create_game(game_id=game_id, game_name=req.game_name, rules=req.rules, creator_id=req.creator_id)
        return {
            "message": f"Game '{game_id}' created.",
            "game_id": game_id,
            "game_name": req.game_name,
            "creator_id": req.creator_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/list", response_model=List[GameSummaryResponse])
def get_all_games():
    return manager.get_all_games()

@router.get("/list/{game_id}", response_model=GameSummaryResponse)
def get_game(game_id):
    return manager.get_game(game_id)
    
@router.post("/register", response_model=SuccessResponse)
def register_player(req: RegisterPlayerRequest):
    try:
        manager.register_player(req.game_id, req.player_id, req.player_name, req.power)
        return SuccessResponse(message=f"Player '{req.player_id}' registered for game '{req.game_id}'.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/{game_id}/start", response_model=SuccessResponse)
def start_game(game_id: str):
    # result = manager.start_game(game_id)
    # if result["success"]:
    #     automation.start_automation(game_id)
    return SuccessResponse(data={"game_id": game_id}, message=f"Game {game_id} started")
    
@router.post("/{game_id}/stop", response_model=SuccessResponse)
def stop_game(game_id: str):
    if game_id not in automation.running_games:
        raise HTTPException(status_code=400, detail="Automation not running for this game.")
    automation.stop_automation(game_id)
    return SuccessResponse(message=f"Game '{game_id}' automation stopped.")

@router.post("/{game_id}/orders", response_model=SuccessResponse)
def submit_orders(
    game_id: str = Path(...),
    req: SubmitOrdersRequest = ...
):
    try:
        manager.submit_orders(game_id, req.player_id, req.orders)
        return SuccessResponse(message="Orders submitted successfully.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{game_id}/orders", response_model=SuccessResponse)
def get_orders(req: GetOrdersRequest):
    try:
        orders = manager.get_orders(req.game_id)
        return SuccessResponse(message=f"Orders for game: {req.game_id}", data={"orders": orders})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{game_id}/valid-orders", response_model=SuccessResponse)
def get_valid_orders(game_id: str, power: str):
    try:
        valid_orders = manager._get_power_orders(game_id, power)
        return SuccessResponse(
            message=f"Valid orders for power: {power}",
            data={"valid_orders": valid_orders}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{game_id}/power-units", response_model=SuccessResponse)
def get_power_units(game_id: str, power: str = Query(...)):
    try:
        power_units = manager.get_power_units(game_id, power)
        return SuccessResponse(
            message=f"Units for power: {power}",
            data={"power_units": power_units}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{game_id}/build-orders")
def get_build_orders(game_id: str, power: str = Query(...)):
    try: 
        build_orders = manager.get_build_orders(game_id, power)
        return build_orders
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{game_id}/phase-type")
def get_phase_type(game_id: str):
    try: 
        phase_type = manager.get_phase_type(game_id)
        return phase_type
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/{game_id}/resolve", response_model=SuccessResponse)
def resolve_phase(game_id: str):
    try:
        manager.resolve_game_phase(game_id)
        return SuccessResponse(message=f"Phase resolved for game '{game_id}'.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{game_id}/state", response_model=GameStateResponse)
def get_game_state(game_id: str):
    try:
        state = manager.get_game_state(game_id)
        return GameStateResponse(game_id=game_id, state=state)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.get("/{game_id}/render", response_model=GameRender)
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
    