# Wraps the Diplomacy game engine 

import random 
from diplomacy.engine.game import Game
from diplomacy.engine.power import Power
from diplomacy.engine.map import Map
from diplomacy.utils.export import to_saved_game_format

# the standard diplomacy powers 
DIPLOMACY_POWERS = ["AUSTRIA", "ENGLAND", "FRANCE", "GERMANY", "ITALY", "RUSSIA", "TURKEY"]

class GameManager:
    def __init__(self):
        self.games = {} 
        
    def create_game(self, game_id: str, rules: dict = None):
        if game_id in self.games: 
            raise ValueError(f"Game with ID '{game_id}' already exists.")
        
        if rules is None:
            rules=[
            "CD_DUMMIES",
            "ALWAYS_WAIT",
            "POWER_CHOICE",
            "IGNORE_ERRORS",
            "NO_DEADLINE",
            "NO_PRESS"
        ]

        game = Game(game_id=game_id, rules=rules)
        self.games[game_id] = {
            "game": game,
            "players": {},
            "submitted_orders": {}
        }
        self._save_game_to_db(game_id) # stub
        # TODO change game status
            
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
        
        players[player_id] = power
        
        # get the power object
        power_object = game.get_power(power)
        
        # set as controlled by player
        power_object.set_controlled(player_id)
        
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
        
    def submit_orders(self, game_id: str, player_id: str, orders: list):
        # validate that the game exists, and get data 
        data = self._get_game_data(game_id)
        game = data["game"]
        players = data["players"]
        power = players[player_id]
        
        # validate the player
        if player_id not in players:
            raise ValueError(f"Player '{player_id}' is not registered in this game.")
        
        # check if units belong to player
        # TODO find a way to implement this 
        # Regex doesnt really work, maybe reformat the way that orders are submitted? 
        
        # player_units = game.get_units(power)
        # order_units = 
        
        # validate orders with helper func 
        validated_orders = self.validate_orders(game_id=game_id, orders=orders)
    
        print("Power submitting orders: ", power)
        
        game.set_orders(power, validated_orders, expand=False, replace=True)
        
    def validate_orders(self, game_id: str, orders):
        """
        Returns a list of valid orders, validated against game.get_all_possible_orders()
        """
        data = self._get_game_data(game_id)
        game = data["game"]
        valid_orders_dict = game.get_all_possible_orders()
        
        # flatten orders dict into a set 
        valid_order_set = set()
        for loc_orders in valid_orders_dict.values():
            valid_order_set.update(loc_orders)
            
        # check validity and return 
        valid_orders = [order for order in orders if order in valid_order_set]
        return valid_orders
        
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
            
    def _handle_game_end(self, game_id: str):
        """
        Handles the end of the game (e.g., declare winner, cleanup).
        """
        
        print(f"Game '{game_id}' has ended.")
        # add additional logic here 
        self._save_game_to_db(game_id) # save final state of the game
            
    def get_game(self, game_id: str) -> Game:
        return self._get_game_data(game_id)["game"]
    
    def get_game_state(self, game_id: str):
        data = self._get_game_data(game_id)
        game = data["game"]
        
        return game.get_state()
    
    def render_game(self, game_id: str):
        data = self._get_game_data(game_id)
        game = data["game"]
        
        output_path = "/Users/matthewthompson/repos/diplomacy-backend/app/renders/render.svg"
        game.render(incl_orders=True, incl_abbrev=False, output_format='svg', output_path=output_path)
        
    def _get_game_data(self, game_id: str):
        if game_id not in self.games: 
            raise ValueError(f"Game '{game_id}' not found.")
        return self.games[game_id]
        
    def _save_game_to_db(self, game_id: str):
        """ Placeholder for saving to DB. Will pickle and persist later. """
        print(f"Game '{game_id}' would be saved here.")