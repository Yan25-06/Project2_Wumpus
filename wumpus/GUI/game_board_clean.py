import tkinter as tk
from tkinter import ttk, messagebox
import time
from ..core.environment import Environment
from ..agents.random_agent import RandomAgent
from ..agents.hybrid_agent import HybridAgent
from .setup_ui import SetupUI
from .draw_ui import DrawUI
from .button_functions import ButtonFunctions

class GameBoardUI(tk.Tk):
    def __init__(self, width=8, height=8, seed=None):
        super().__init__()
        self.title("Wumpus World Game Board")
        
        # Disable window resizing and maximize button
        self.resizable(False, False)
        
        # Make window fullscreen
        #self.state('zoomed')  # For Windows
        
        # Board Frame
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        print(f"Screen size: {screen_width}x{screen_height}") 
        self.width = width
        self.height = height
        
        # Calculate cell size based on screen size
        # Leave space for controls panel on right (about 400px) and margins
        available_width = screen_width - 600  # Reserve more space for right panel
        available_height = screen_height - 250  # Leave space for title and margins
        
        # Calculate optimal cell size - dynamically based on board size
        max_cell_width = available_width // self.width
        max_cell_height = available_height // self.height
        self.cell_size = min(max_cell_width, max_cell_height, 120)  # Cap at 120px for small boards
        print(f"Initial board size: {self.width}x{self.height}, Cell size: {self.cell_size}px")  # Debugging output 
        
        # Initialize environment and agent
        # Agent mode and game settings variables
        self.agent_mode = "Hybrid"  # Default to Hybrid
        self.board_size = 8  # Default board size
        self.pit_probability = 0.2  # Default pit probability (20%)
        self.wumpus_count = 2  # Default number of wumpus
        
        self.seed = seed if seed is not None else 1  # Default seed to 1
        print(self.seed)
        self.env = Environment(N=self.board_size, K=self.wumpus_count, 
                              pit_prob=self.pit_probability, seed=self.seed)
        self.agent = HybridAgent(self.env)
        self.game_running = False
        self.game_over = False
        self.moves_history = []  # Track all agent moves
        
        # Initialize UI components
        self.setup_ui_handler = SetupUI(self)
        self.draw_ui = DrawUI(self)
        self.button_functions = ButtonFunctions(self)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI using the SetupUI handler"""
        self.setup_ui_handler.setup_ui()
        
        # Create a dummy agent button reference for settings to update
        # Since agent selection is now in settings, we create a Label to show current agent
        agent_info_frame = ttk.Frame(self.left_frame)
        agent_info_frame.pack(pady=(10, 0))
        
        ttk.Label(agent_info_frame, text="Current Agent:", font=('Arial', 10, 'bold')).pack()
        self.agent_button = ttk.Label(agent_info_frame, text=f"AGENT: {self.agent_mode}", 
                                     font=('Arial', 10), relief='sunken', padding=5)
        self.agent_button.pack()
        
        # Draw initial board
        self.draw_ui.draw_board()
        self.draw_ui.update_display()
        
        # Add initial position to moves history
        initial_percepts = self.env.get_percepts(self.agent.x, self.agent.y)
        self.draw_ui.add_move_to_history("Start", (self.agent.x, self.agent.y), self.agent.dir, "GAME BEGIN")
    
    # Delegate button functions to ButtonFunctions class
    def single_step(self):
        return self.button_functions.single_step()
    
    def start_game(self):
        return self.button_functions.start_game()
    
    def stop_game(self):
        return self.button_functions.stop_game()
    
    def reset_game(self):
        self.seed += 1
        return self.button_functions.reset_game(seed=self.seed)
    
    def change_board_size(self):
        return self.button_functions.change_board_size()
    
    def compare_agents(self):
        return self.button_functions.compare_agents()
    
    def run_agent(self):
        return self.button_functions.run_agent()


def main():
    app = GameBoardUI()
    app.mainloop()


if __name__ == "__main__":
    main()
