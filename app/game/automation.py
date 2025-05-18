# controls game loop, phase resolution, bots, etc

import time
from threading import Thread 
from .game_manager import GameManager

class GameAutomation:
    def __init__(self, manager: GameManager):
        self.manager = manager
        self.running_games = {}
        self.stop_flags = {}
        
    def start_automation(self, game_id: str, interval: int = 60):
        if game_id in self.running_games:
            print(f"Automation already running for {game_id}")
            return 
        
        self.stop_flags[game_id] = False
        thread = Thread(target=self._run_loop, args=(game_id, interval), daemon=True)
        self.running_games[game_id] = thread
        thread.start()
        
    def stop_automation(self, game_id: str):
        if game_id in self.running_games:
            self.stop_flags[game_id] = True
            print(f"[{game_id}] stop signal sent to automation.")
        else: 
            print(f"[{game_id}] No running automation to stop.")
        
    def _run_loop(self, game_id: str, interval: int):
        print(f"[{game_id}] Automation started.")
        while not self.stop_flags.get(game_id, True): 
            try:
                game_state = self.manager.get_game_state(game_id)
                if not game_state["success"]:
                    print(f"[{game_id}] Error: {game_state['error']}")
                    break
                
                game = self.manager._get_game_object(game_id)
                if game.is_game_done:
                    print(f"[{game_id}] Game finished.")
                    break
                
                # submit bot orders 
                self.manager._create_bot_orders(game_id)
                
                # Check if all players have submitted orders 
                
                # advance phase 
                self.manager.resolve_game_phase(game_id)
                
                # wait for next tick 
                time.sleep(interval)
                
            except Exception as e:
                print(f"[{game_id}] Automation error: {e}")
                break
            
        print(f"[{game_id}] Automation stopped.")
        self.running_games.pop(game_id, None)
        self.stop_flags.pop(game_id, None)