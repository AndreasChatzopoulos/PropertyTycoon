from game import Game

# Load players from file
player_names, player_tokens = Game.load_players_from_file("players.json")

# Start the game
game = Game(player_names, player_tokens)
game.play_turn()

