# Wraps the Diplomacy game engine 

import random 
from diplomacy.engine.game import Game
from diplomacy.engine.map import Map
from diplomacy.utils.export import to_saved_game_format

# the standard diplomacy powers 
DIPLOMACY_POWERS = ["AUSTRIA", "ENGLAND", "FRANCE", "GERMANY", "ITALY", "RUSSIA", "TURKEY"]

class GameManager:
    def __init__(self):
        self.games = {} 
        
    def create_game(self, game_id: str, rule_options: dict = None):
        if game_id in self.games: 
            raise ValueError(f"Game with ID '{game_id}' already exists.")
        game = Game(game_id=game_id, rule_options=rule_options or {})
        self.games[game_id] = {
            "game": game,
            "players": {},
            "submitted_orders": {}
        }
        self._save_game_to_db(game_id) # stub
            
    def register_player(self, game_id: str, player_id: str, power: str = None): 
        data = self._get_game_data(game_id)
        game = data["game"]
        players = data["players"]
            
        if player_id in players:
            raise ValueError(f"Player '{player_id}' already registered.")
            
        assigned_powers = set(players.values())
        available_powers = [p for p in DIPLOMACY_POWERS if p not in assigned_powers]
            
        if not available_powers: 
            raise ValueError("All powers already assigned.")
            
        # If no power assigned, assign one randomly 
        if power is None: 
            power = random.choice(available_powers)
        elif power not in available_powers: 
            raise ValueError(f"Power '{power}' is already taken or invalid.")
            
        if not game.has_power(power):
            raise ValueError(f"Power '{power}' does not exist in game.")
        
        players[player_id] = power
        self._save_game_to_db(game_id) #stub
            
    def start_game(self, game_id: str):
        data = self._get_game_data(game_id)
        game = data["game"]
        players = data["players"]
            
        if len(players) < 2:
            raise ValueError("At least 2 players are required to start a game.")
            
        if len(players) < 7:
            print("Warning: Game started with fewer than 7 players.")
            
        game.process() #advance to first phase
        self._save_game_to_db(game_id) #stub 
        return self.get_public_game_state(game_id)
        
    def submit_orders(self, game_id: str, player_id: str, orders: dict):
        # validate that the game exists, and get data 
        data = self._get_game_data(game_id)
        game = data["game"]
        players = data["players"]
        submitted_orders = data.setdefault("submitted_orders", {})
        
        # validate the player
        if player_id not in players:
            raise ValueError(f"Player '{player_id}' is not registered in this game.")
        
        power = players[player_id]
        
        # check if this power has already submitted orders 
        if power in submitted_orders:
            raise ValueError(f"Orders for power '{power}' already submitted for this phase.")
        
        # check phase type (only allowed during movement or retreat)
        phase_type = game.get_current_phase()[-1]
        if phase_type not in ['M', 'R']:
            raise ValueError(f"Cannot submit orders during '{game.get_current_phase()}' phase.")
        
        
        # convert simple format
        formatted_orders = [f"{unit} - {destination}" for unit, destination in orders.items()]
        
        # basic validation: units owned by power 
        power_units = game.get_units(power)
        for unit in orders:
            if unit not in power_units:
                raise ValueError(f"Unit '{unit}' does not belong to power '{power}'")
            
        # store the orders 
        submitted_orders[power] = formatted_orders
        print(f"[OK] Orders submitted for power '{power}': {formatted_orders}")
        
    def resolve_game_phase(self, game_id: str):
        """
        Resolves the current phase by processing all orders and updating the game state.
        """
        
        # get the game and current phase 
        data = self._get_game_data(game_id)
        game = data["game"]
        current_phase = game.get_current_phase()
        
        print(f"Resolving phase: {current_phase}")
        
        # ensure that the phase is resolvable (movement or retreat)
        phase_type = current_phase[-1]
        if phase_type not in ["M", "R"]:
            raise ValueError(f"Cannot resolve during '{current_phase}' phase")
        
        submitted_orders = data["submitted_orders"]
        all_powers = game.get_map_power_names()  # all playable powers

        for power in all_powers:
            if power in submitted_orders:
                orders = submitted_orders[power]
            else:
            # Generate hold orders for each unit of this power
                units = game.get_units(power)
                orders = [f"{unit} H" for unit in units]
                print(f"[AUTO] Submitting HOLD orders for power '{power}': {orders}")
        
            game.set_orders(power, orders)  
        
        # process the orders for the current phase
        game.process()
        
        # Clear submitted orders after processing
        data["submitted_orders"].clear()
        
        self._save_game_to_db(game_id) # stub 
        
        # check if the game is done after processing orders 
        if game.is_game_done:
            self._handle_game_end(game_id)
        return self.get_public_game_state(game_id)
            
    def _handle_game_end(self, game_id: str):
        """
        Handles the end of the game (e.g., declare winner, cleanup).
        """
        
        print(f"Game '{game_id}' has ended.")
        # add additional logic here 
        self._save_game_to_db(game_id) # save final state of the game
            
    def get_game(self, game_id: str) -> Game:
        return self._get_game_data(game_id)["game"]
    
    def get_public_game_state(self, game_id: str) -> dict:
        """
        Retrieves a simplified representation of the current map state.
        """
        game = self.get_game(game_id)
        
        # get the phase of the game 
        phase = game.get_current_phase()
        
        # get the powers and units
        units = game.get_units()
        centers = game.get_centers() # can be filteres by power if needed 
        
        return {
            "phase": phase,
            "units": units,
            "centers": centers,          # Centers controlled by powers
            "controlled_powers": game.get_controlled_power_names(""), # List all controlled powers
        }
        
    def get_game_metadata(self, game_id: str) -> dict:
        """
        Returns high-level metadata about the game, for display and debugging.
        Does not expose full internal game state.
        """
        data = self._get_game_data(game_id)
        game = data["game"]
        players = data["players"]
        submitted_orders = data.get("submitted_orders", {})
    
        assigned_powers = set(players.values())
        all_powers = set(DIPLOMACY_POWERS)
        available_powers = list(all_powers - assigned_powers)
    
        # Determine status
        if game.is_game_done:
            status = "done"
        else:
            status = "in_progress"
    
        # Powers missing orders (only meaningful if game in progress)
        unsubmitted_powers = []
        if status == "in_progress":
            current_phase = game.get_current_phase()
            phase_type = current_phase[-1]
            if phase_type in ['M', 'R']:  # only relevant for phases that require orders
                powers_expected = game.get_map_power_names()
                unsubmitted_powers = [p for p in powers_expected if p not in submitted_orders]

        return {
            "game_id": game_id,
            "phase": game.get_current_phase(),
            "status": status,
            "players": players,                      # {player_id: power}
            "assigned_powers": list(assigned_powers),
            "available_powers": available_powers,
            "submitted_orders": list(submitted_orders.keys()),
            "missing_orders": unsubmitted_powers,
            "player_count": len(players),
            "warnings": ["Game has fewer than 7 players"] if len(players) < 7 else [],
        }
        
    def get_bot_game_info(self, game_id: str, player_id: str):
        """
        Retrieves all relevant game data needed by a bot to make decisions for its turn. 
        """
        data = self._get_game_data(game_id)
        game = data["game"]
        players = data["players"]
        
        if player_id not in players: 
            raise ValueError(f"Player '{player_id}' is not registered in this game.")
        
        power = players[player_id]
        
        # retrieve current phase of the game 
        phase = game.get_current_phase()
        phase_type = phase[-1] # movement or retreat phase 
        
        # retrieve all units controlled by the bot
        bot_units = game.get_units(power)
        
        # retrieve all enemy units (exclude bot's own power)
        enemy_units = {power: game.get_units(power) for power in game.get_map_power_names() if power != bot_units}
        
        # retrieve all centers and which are controlled by the bot or enemies 
        centers = game.get_centers()
        controlled_centers = {center: power for center, power in centers.items()}
        
        # orders submitted so far
        submitted_orders = data["submitted_orders"] 
        bot_orders = submitted_orders.get(power, [])
                        
        game_status = "done" if game.is_game_done else "in_progress"
        
        # return everything the bot needs 
        return {
            "phase": phase,
            "phase_type": phase_type,
            "bot_units": bot_units,
            "enemy_units": enemy_units,
            "controlled_centers": controlled_centers,
            "submitted_orders": bot_orders,
            "game_status": game_status,
            "all_powers": game.get_map_power_names(),
            "available_powers": [p for p in DIPLOMACY_POWERS if p not in players.values()] 
        }
        
    def _get_game_data(self, game_id: str):
        if game_id not in self.games: 
            raise ValueError(f"Game '{game_id}' not found.")
        return self.games[game_id]
        
    def _save_game_to_db(self, game_id: str):
        """ Placeholder for saving to DB. Will pickle and persist later. """
        print(f"Game '{game_id}' would be saved here.")