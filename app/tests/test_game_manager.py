import unittest
from unittest.mock import patch
from game_manager import GameManager  # Make sure this path is correct

class TestGameManager(unittest.TestCase):
    def setUp(self):
        """Runs before each test. Creates a fresh game instance."""
        self.manager = GameManager()
        self.game_id = "test_game"
        self.manager.create_game(self.game_id)

    def test_player_registration(self):
        """Players should be able to register with a valid power."""
        self.manager.register_player(self.game_id, "alice", "FRANCE")
        self.manager.register_player(self.game_id, "bob", "ENGLAND")

        players = self.manager._get_game_data(self.game_id)["players"]
        self.assertEqual(players["alice"], "FRANCE")
        self.assertEqual(players["bob"], "ENGLAND")
        
    def test_duplicate_game_creation(self):
        with self.assertRaises(ValueError):
            self.manager.create_game(self.game_id)
            
    def test_random_power_assignment(self):
        DIPLOMACY_POWERS = ["AUSTRIA", "ENGLAND", "FRANCE", "GERMANY", "ITALY", "RUSSIA", "TURKEY"]
        self.manager.register_player(self.game_id, "alice")
        assigned_power = self.manager._get_game_data(self.game_id)["players"]["alice"]
        self.assertIn(assigned_power, DIPLOMACY_POWERS)

    def test_duplicate_registration(self):
        """Registering the same player twice should raise an error."""
        self.manager.register_player(self.game_id, "alice", "FRANCE")
        with self.assertRaises(ValueError):
            self.manager.register_player(self.game_id, "alice", "ENGLAND")

    def test_order_submission_and_resolution(self):
        """Players can submit valid orders, which get resolved correctly."""
        self.manager.register_player(self.game_id, "alice", "FRANCE")
        self.manager.register_player(self.game_id, "bob", "ENGLAND")
        self.manager.start_game(self.game_id)

        orders_france = {
            "A PAR": "BUR",
            "A MAR": "SPA",
            "F BRE": "MAO"
        }
        orders_england = {
            "F LON": "NTH",
            "F EDI": "NWG",
            "A LVP": "YOR"
        }

        self.manager.submit_orders(self.game_id, "alice", orders_france)
        self.manager.submit_orders(self.game_id, "bob", orders_england)

        with self.assertRaises(ValueError):
            # Can't submit orders twice in the same phase
            self.manager.submit_orders(self.game_id, "alice", orders_france)

        self.manager.resolve_game_phase(self.game_id)
        state = self.manager.get_public_game_state(self.game_id)
        self.assertIn("phase", state)
        self.assertIn("units", state)

    def test_unregistered_player_submission(self):
        """Only registered players can submit orders."""
        self.manager.register_player(self.game_id, "alice", "FRANCE")
        self.manager.register_player(self.game_id, "player2", "ENGLAND")
        self.manager.start_game(self.game_id)

        orders = {"A PAR": "BUR"}
        with self.assertRaises(ValueError):
            self.manager.submit_orders(self.game_id, "bob", orders)

    def test_invalid_unit_submission(self):
        """Players can't submit orders for units they don't own."""
        self.manager.register_player(self.game_id, "alice", "FRANCE")
        self.manager.register_player(self.game_id, "bob", "ENGLAND")
        self.manager.start_game(self.game_id)

        invalid_orders = {"A BER": "MUN"}  # France does not own A BER
        with self.assertRaises(ValueError):
            self.manager.submit_orders(self.game_id, "alice", invalid_orders)

    def test_game_end_handling(self):
        """If the game is over, resolution should finalize and save state."""
        self.manager.register_player(self.game_id, "alice", "FRANCE")
        self.manager.register_player(self.game_id, "bob", "ENGLAND")
        self.manager.start_game(self.game_id)

        # Manually mark game as over
        game = self.manager.get_game(self.game_id)
         # game.set_game_done(True)

        self.manager.resolve_game_phase(self.game_id)

    def test_get_public_game_state(self):
        """The map state should be accessible even before orders are submitted."""
        self.manager.register_player(self.game_id, "alice", "FRANCE")
        self.manager.register_player(self.game_id, "bob", "ENGLAND")
        self.manager.start_game(self.game_id)

        state = self.manager.get_public_game_state(self.game_id)
        self.assertIn("phase", state)
        self.assertIn("units", state)
        
    def test_get_bot_game_info(self):
        """Test that the bot receives the correct game information to make a move."""
        # Register players, with one as a bot.
        self.manager.register_player(self.game_id, "alice", "FRANCE")
        self.manager.register_player(self.game_id, "bot", "GERMANY")  # Registering the bot as "bot"
        self.manager.start_game(self.game_id)

        # Assuming 'get_bot_game_info()' is implemented to return data for the bot to make decisions
        bot_game_info = self.manager.get_bot_game_info(self.game_id, "bot")  

        # Validate that the bot gets the right information
        self.assertIn("phase", bot_game_info)  # Make sure the game phase is included
        self.assertIn("bot_units", bot_game_info)  # Bot's units should be included
        self.assertIn("controlled_centers", bot_game_info)  # Controlled centers should be listed

        # You could validate specific data as well, depending on what 'get_bot_game_info' returns
        # For example, checking that the bot has the correct units or controlled centers
        self.assertIn("A BER", bot_game_info["bot_units"])  # Assuming bot controls Berlin (A BER)
        self.assertIn("BER", bot_game_info["controlled_centers"]["GERMANY"])  # Assuming Berlin is a controlled center
        
    def test_game_metadata_reporting(self):
        self.manager.register_player(self.game_id, "alice", "FRANCE")
        self.manager.register_player(self.game_id, "bob", "ENGLAND")
        self.manager.start_game(self.game_id)

        metadata = self.manager.get_game_metadata(self.game_id)
        self.assertEqual(metadata["status"], "in_progress")
        self.assertIn("FRANCE", metadata["missing_orders"])
        self.assertIn("ENGLAND", metadata["missing_orders"])


if __name__ == '__main__':
    unittest.main()