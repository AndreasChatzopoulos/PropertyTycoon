import threading
import queue
import main
import main_terminal

# Queues for communication between GUI and game logic
gui_to_game = queue.Queue()
game_to_gui = queue.Queue()

def start_gui():
    # Create and run the GUI instance
    gui = main.MonopolyGUI(gui_to_game, game_to_gui)
    gui.run()

def start_game():
    # Create and run the game logic instance
    game = main_terminal.MonopolyGame(gui_to_game, game_to_gui)
    game.run()

def controller():
    # Start both GUI and game logic in separate threads
    gui_thread = threading.Thread(target=start_gui, daemon=True)
    game_thread = threading.Thread(target=start_game, daemon=True)
    gui_thread.start()
    game_thread.start()

controller()
