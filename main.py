from game import Game

# Load players from file
player_names, player_tokens, player_identities = Game.load_players_from_file("players.json")

# Start the game
game = Game(player_names, player_tokens, player_identities)
game.play_turn()


"""pygame start - wont work with input() calls pygame freezes"""
if __name__ == "__main__":
    try:
        game_gui = GameGUI()
        game_gui.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit()