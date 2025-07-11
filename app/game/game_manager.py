# Wraps the Diplomacy game engine 

import random 
from datetime import datetime, timezone
from diplomacy.engine.game import Game
from diplomacy.utils.export import to_saved_game_format

# the standard diplomacy powers 
DIPLOMACY_POWERS = ["AUSTRIA", "ENGLAND", "FRANCE", "GERMANY", "ITALY", "RUSSIA", "TURKEY"]

class GameManager:
    def __init__(self):
        self.games = {} 
        
    def get_all_games(self):
        game_list = []
        for game_id, game_data in self.games.items():
            game_list.append({
                "game_id": game_id,
                "players": game_data["players"],
                "game_name": game_data["game_name"],
                "creator_id": game_data["creator_id"]
            })
        return game_list
    
    def get_game(self, game_id: str):
        if game_id in self.games:
            game_data = self.games[game_id]
            return {
                "game_id": game_id,
                "players": game_data["players"],
                "game_name": game_data["game_name"],
                "creator_id": game_data["creator_id"]
                
            }
        return None
            
        
    def create_game(self, game_id: str, game_name: str, creator_id: str, rules: dict = None):
        """
        Creates a new game with 7 dummies for all powers.
        Generic rules. 
        Saves game to db. 
        TODO: Return values. 
        """
        if game_id in self.games: 
            return {"success": False, "error": f"Game with ID '{game_id}' already exists."}
        
        if rules is None:
            rules=[
            "CD_DUMMIES",
            "ALWAYS_WAIT",
            "POWER_CHOICE",
            "IGNORE_ERRORS",
            "NO_DEADLINE",
            "NO_PRESS"
        ]

        game = Game(game_id=game_id, rules=rules, creator_id=creator_id)
        self.games[game_id] = {
            "game": game,
            "players": {},
            "game_name": game_name,
            "creator_id": creator_id
        }
        self._save_game_to_db(game_id) # stub
        print(self.games)
        
        return {"success": True, "game_id": game_id, "rules": rules}
            
    def register_player(self, game_id: str, player_id: str, player_name: str, power: str = None): 
        """
        Registers a new player, with ID and power. 
        Sets power to be controlled by player. 
        TODO: Figure out how to remove dummy. 
        """
        try: 
            data = self._get_game_data(game_id)
            game = self._get_game_object(game_id)
        except ValueError as e:
            return {"success": False, "error": str(e)}
        
        
        players = data["players"]
        if player_id in players:
            return {"success": False, "error": f"Player '{player_id}' already registered."}
            
        assigned_powers = set(player["power"] for player in players.values())
        available_powers = [p for p in DIPLOMACY_POWERS if p not in assigned_powers]
            
        if not available_powers: 
            return {"success": False, "error": "All powers already assigned."}
            
        # If no power assigned, assign one randomly 
        if power is None: 
            power = random.choice(available_powers)
        elif power not in available_powers: 
            return {"success": False, "error": f"Power '{power}' is already taken or invalid."}
        
        players[player_id] = {
            "power": power,
            "name": player_name,
        }
        
        # get the power object
        power_object = game.get_power(power)
        
        # set as controlled by player
        power_object.set_controlled(player_id)
        
        self._save_game_to_db(game_id) #stub
        
        return {"success": True, "player_id": player_id, "player_name": player_name, "power": power}
            
    def start_game(self, game_id: str):
        """
        Starts the game (set status to active).
        Saves the game to db.
        """
        try: 
            data = self._get_game_data(game_id)
            game = self._get_game_object(game_id)
        except ValueError as e:
            return {"success": False, "error": str(e)}
        
        # if len(data["players"]) < 2:
        #     return {"success": False, "error": "At least 2 players are required to start a game."}
           
        # game.process() #advance to first phase
        game.set_status("active")
        self._save_game_to_db(game_id) #stub 
        
        return {"success": True, "status": "active", "message": "Game started successfully."}
        
    def submit_orders(self, game_id: str, player_id: str, orders: list):
        """
        Submits orders for a specific power. 
        Validates if moves are valid moves. 
        """
        # validate that the game exists, and get data 
        try: 
            data = self._get_game_data(game_id)
            game = self._get_game_object(game_id)
            players = data["players"]
        except ValueError as e:
            return {"success": False, "error": str(e)}
            
        if player_id not in players:
            return {"success": False, "error": f"Player '{player_id}' is not registered."} 
           
        power = players[player_id]['power']
        # validate orders with helper func 
        # validated_orders = self.validate_orders(game_id=game_id, orders=orders, power=power)
        
        # if not validated_orders:
        #     return {"success": False, "error": "No valid orders submitted."}
        
        game.set_orders(power, orders, expand=False, replace=True)
        
        print(f"All submitted orders: {game.get_orders()}")
        
        return {"success": True, "power": power, "orders_submitted": orders}
        
    def validate_orders(self, game_id: str, orders, power):
        """
        Returns a list of valid orders, validated against game.get_all_possible_orders(), filtered by power
        """
        valid_power_orders = self._get_power_orders(game_id=game_id, power=power)
            
        # check validity and return 
        valid_orders = [order for order in orders if order in valid_power_orders]
        return valid_orders
    
    def get_orders(self, game_id: str):
        """
        Returns all submitted orders for the current phase
        """
        game = self._get_game_object(game_id)
        orders = game.get_orders()
        return orders
        
    def resolve_game_phase(self, game_id: str):
        """
        Resolves the current phase by processing all orders and updating the game state.
        TODO: Return values
        """
        
        # get the game and current phase 
        try:
            data = self._get_game_data(game_id)
            game = self._get_game_object(game_id)
        except ValueError as e:
            return {"success": False, "error": str(e)}
        
        
        current_phase = game.get_current_phase()
        # ensure that the phase is resolvable (movement or retreat)
        # phase_type = current_phase[-1]
        # if phase_type not in ["M", "R"]:
        #     return {"success": False, "error": f"Cannot resolve during '{current_phase}' phase"}
        
        all_powers = game.get_map_power_names()  # all powers   
        
        # self._create_bot_orders(game_id)     

        # For unsubmitted powers, fill in HOLD orders
        for power in all_powers:
            if not game.get_orders(power):
                units = game.get_units(power)
                hold_orders = [f"{unit} H" for unit in units]
                print(f"[AUTO] Submitting HOLD orders for power '{power}': {hold_orders}")
                game.set_orders(power, hold_orders)
        
        
        # process the orders for the current phase
        game.process()
        
        # Clear submitted orders after processing (BROKEN)
        # data["submitted_orders"].clear()
        
        self._save_game_to_db(game_id) # stub 
        
        status = "complete" if game.is_game_done else "active"
        
        # check if the game is done after processing orders 
        if game.is_game_done:
            self._handle_game_end(game_id)
            
        return {
            "success": True,
            "phase": current_phase,
            "status": status,
            "next_phase": game.get_current_phase()
        }
            
    def get_phase_type(self, game_id: str):
        """
        returns the phase type 
        """
        game = self._get_game_object(game_id)
        return game.phase_type
            
    def _handle_game_end(self, game_id: str):
        """
        Handles the end of the game (e.g., declare winner, cleanup).
        """
        
        print(f"Game '{game_id}' has ended.")
        # add additional logic here 
        self._save_game_to_db(game_id) # save final state of the game
    
    def get_game_state(self, game_id: str) -> dict:
        try:
            game = self._get_game_object(game_id)
            return {"success": True, "state": game.get_state()}
        except ValueError as e:
            return {"success": False, "error": str(e)}
    
    def render_game(self, game_id: str):
        """
        Renders the game with the built in engine render
        Probably not good enough for prod, but nice for MVP
        """
        game = self._get_game_object(game_id)
        output_path = f"/tmp/{game_id}.svg"
        game.render(incl_orders=True, incl_abbrev=False, output_format='svg', output_path=output_path)
        return output_path
        
    def save_game(self, game_id: str):
        """
        Saves the game into the app/saves folder. 
        TODO: Return values. 
        """
        # STUB
        
    def _get_power_orders(self, game_id: str, power):
        """
        Gets all valid moves for a specific power 
        
        Args: game_id, power 
        
        Returns: A list of valid orders
        """
        game = self._get_game_object(game_id)
        valid_orders_dict = game.get_all_possible_orders()
        power_units = game.get_units(power)
        
        # flatten orders dict into a set 
        valid_order_set = set()
        for loc_orders in valid_orders_dict.values():
            valid_order_set.update(loc_orders)
            
        matching_orders = [order for order in valid_order_set if any(unit in order for unit in power_units)]
        
        return matching_orders
    
    def get_power_units(self, game_id: str, power):
        """
        Gets all units belonging to a power
        
        Returns: list of units
        """
        game = self._get_game_object(game_id)
        power_units = game.get_units(power)
        return power_units
    
    def get_build_orders(self, game_id: str, power):
        """
        Gets possible build orders for a power 
        """
        game = self._get_game_object(game_id)
        power_obj = game.get_power(power)
        
        print(power_obj.adjust)
        
    
    def _remove_character(text, char):
        """
        Removes all occurrences of a character from a string 
        
        Misc string sanitation
        """
        
        return text.replace(char, "")
    
        
    def _get_game_data(self, game_id: str):
        """
        Deprecated: moving to _get_game_object()
        """
        if game_id not in self.games: 
            raise ValueError(f"Game '{game_id}' not found.")
        return self.games[game_id]
        
    def _save_game_to_db(self, game_id: str):
        """ Placeholder for saving to DB. Will pickle and persist later. """
        print(f"Game '{game_id}' would be saved here.")
        
    def _get_game_object(self, game_id: str):
        """
        Gets the game object for the game with relevant game_id
        """
        if game_id not in self.games:
            raise ValueError(f"Game '{game_id}' not found.")
        data = self.games[game_id]
        return data["game"]
    
    # Maybe replace above with this? 
    # def get_game(self, game_id: str) -> Game:
    #     return self._get_game_data(game_id)["game"]
    
    def get_unassigned_powers(self, game_id: str) -> list:
        """
        Returns a list of powers that do not have an assigned player
        """
        data = self._get_game_data(game_id)
        assigned_powers = set(player["power"] for player in data["players"].values())
        return [power for power in DIPLOMACY_POWERS if power not in assigned_powers]
    
    def _create_bot_orders(self, game_id: str):
        """
        Loops over dummy powers, gets a valid order for each power, and submits it. 
        
        Not perfect, skips a lot of units.. but good for now
        """
        dummy_powers = self.get_unassigned_powers(game_id)
        game = self._get_game_object(game_id)
        for power in dummy_powers:
            possible_orders = self._get_power_orders(game_id, power)
            if not possible_orders:
                print(f"No valid orders for {power}")
                continue
            
            chosen_order = random.choice(possible_orders)
            print(f"Chosen random order {chosen_order} for dummy power: {power}")
            
            game.set_orders(power, chosen_order, expand=False, replace=True)