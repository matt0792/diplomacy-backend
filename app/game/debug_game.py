# test runner script so i dont go insane 

import pprint
from diplomacy import Game
from app.game.game_manager import GameManager

game_id = "test_game"
manager = GameManager()
pp = pprint.PrettyPrinter(indent=2, width=80, depth=5)

def print_menu():
    print("\n=== Diplomacy Debug Menu ===")
    print("1. Create game")
    print("1.5 Start game")
    print("2. Register player")
    print("3. Show current phase")
    print("4. Show units")
    print("5. Submit orders")
    print("6. Process phase")
    print("7. Show supply centers")
    print("8. Show game info")
    print("9. Get all possible orders")
    print("9.5. Get all possible orders for power")
    print("10. Get order status")
    print("11. Get power")
    print("12. Get game state")
    print("13. Render game")
    print("14. Save game")
    print("15. Create dummy orders")
    print("============================") 
    
while True:
    print_menu()
    choice = input("Choose an option: ").strip()
    
    if choice == "1":
        manager.create_game(game_id)
        
        print("Game created.")
        data = manager._get_game_data(game_id)
        game = data["game"]
        
    elif choice == "1.5":
        manager.start_game(game_id)
        
        
    elif choice == "2":
        player_id = input("Enter player ID: ").strip()
        power = input("Enter power (e.g. 'ENGLAND', 'FRANCE'): ").strip()
        
        data = manager._get_game_data(game_id)
        game = data["game"]
        
        print(f"Power info before register_player(): {game.get_power(power)}")
        
        manager.register_player(game_id=game_id, player_id=player_id, power=power)
        
        data = manager._get_game_data(game_id)  # get updated state
        game = data["game"]
    
        print(f"Power info after register_player(): {game.get_power(power)}")
        print(f"Player {player_id} registered as {power} in {game_id}")
        
    elif choice == "3":
        phase = manager._get_game_data(game_id)["game"].get_current_phase()
        print("Current phase:", phase)
        
    elif choice == "4":
        power = input("Enter power: ").strip()
        units = manager._get_game_data(game_id)["game"].get_units(power)
        print(units)
        
    elif choice == "5":
        player_id = input("Enter player ID: ").strip()
        order_count = int(input("How many orders? "))
        orders = []
        for _ in range(order_count):
            order = input("Order (e.g. 'F LON - YOR'): ").strip()
            orders.append(order)
        manager.submit_orders(game_id, player_id, orders)
        print("Orders submitted.")
        
    elif choice == "6":
        data = manager._get_game_data(game_id)
        data["game"].process()
            
    elif choice == "7":
        power = input("Enter power: ").strip()
        scs = manager._get_game_data(game_id)["game"].get_supply_centers(power)
        print(f"Supply centers for {power}:", scs)
        
    elif choice == "8":
        data = manager._get_game_data(game_id)
        game = data["game"]
        pp.pprint(game.to_dict())
        print(game)
        
        
    elif choice == "9":
        data = manager._get_game_data(game_id)
        game = data["game"]
        pp.pprint(game.get_all_possible_orders())
        
    elif choice == "9.5":
        power = input("Enter power: ").strip()
        print(f"All possible orders for {power}: {manager._get_power_orders(game_id, power)}")
        
    elif choice == "10":
        data = manager._get_game_data(game_id)
        game = data["game"]
        power = input("Enter power: ").strip()
        pp.pprint(game.get_order_status(power))
        
    elif choice == "11":
        data = manager._get_game_data(game_id)
        game = data["game"]
        power = input("Enter power:").strip()
        power_object = game.get_power(power)
        print(f"Controller: {power_object.get_controller()}")
        print(f"Is Controlled: {power_object.is_controlled()}")
        
    elif choice == "12":
        pp.pprint(manager.get_game_state(game_id))
        
    elif choice == "13":
        print(manager.render_game(game_id))
        print("Game rendered")
        
    elif choice == "14":
        manager.save_game(game_id)
        print("Game saved")
        
    elif choice == "15":
        manager._create_bot_orders(game_id)
        print("Creating bot orders")
        
        
        
    
    else:
        print("Invalid choice.")