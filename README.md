# Diplomacy Backend

A FastAPI wrapper for the diplomacy game engine to allow for fully featured interaction without being bound to the default React web interface. It provides endpoints for creating games, registering players, submitting orders, and rendering game states. Most features are still in heavy development. 

## Project Structure

- `app/`: Main application directory
  - `main.py`: FastAPI entry point
  - `game/`: Game-related functionality
    - `game_manager.py`: Manages game state and logic
    - `automation.py`: Handles game automation
    - `models/`: Data models for the game
      - `pydantic.py`: Pydantic models for request/response handling
  - `tests/`: Unit tests for the application

## Requirements

- Python 3.11
- FastAPI
- Uvicorn
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/matt0792/diplomacy-backend.git
   cd diplomacy-backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To run the application, use the following command:

```bash
uvicorn app.main:app --reload
```

This will start the FastAPI server, and you can access the API documentation at `http://localhost:8000/docs`.

## API Endpoints

- `POST /games`: Create a new game
- `POST /games/{game_id}/register`: Register a player for a game
- `POST /games/{game_id}/start`: Start a game
- `POST /games/{game_id}/stop`: Stop a game
- `POST /games/{game_id}/orders`: Submit orders for a power
- `POST /games/{game_id}/resolve`: Resolve a game phase
- `GET /games/{game_id}/state`: Get the current state of a game
- `GET /games/{game_id}/render`: Render the game state to SVG
