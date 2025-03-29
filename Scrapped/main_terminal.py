from GameElements.game_logic import Game

# Load players from file
player_names, player_tokens, player_identities = Game.load_players_from_file("players.json")

# Start the game
game = Game(player_names, player_tokens, player_identities)
game.play_turn()

