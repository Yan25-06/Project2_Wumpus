import tkinter as tk
from tkinter import ttk, messagebox
import time
from ..core.environment import Environment
from ..agents.random_agent import RandomAgent

class GameBoardUI(tk.Tk):
    def __init__(self, width=8, height=8):
        super().__init__()
        
        self.title("Wumpus World - Random Agent")
        
        # Make window fullscreen
        self.state('zoomed')  # For Windows
        # Alternative for cross-platform:
        # self.attributes('-fullscreen', True)
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        self.width = width
        self.height = height
        
        # Calculate cell size based on screen size
        # Leave space for controls and status (about 300px)
        available_width = screen_width - 100
        available_height = screen_height - 350
        
        # Calculate optimal cell size
        max_cell_width = available_width // self.width
        max_cell_height = available_height // self.height
        self.cell_size = min(max_cell_width, max_cell_height, 120)  # Cap at 120px
        
        # Bind keyboard shortcuts
        self.bind('<Escape>', self.exit_fullscreen)
        self.bind('<F11>', self.toggle_fullscreen)
        
        # Initialize environment and agent
        self.env = Environment()
        self.agent = RandomAgent(self.env)
        self.game_running = False
        self.game_over = False
        self.steps = 0
        self.fullscreen = True
        
        self.setup_ui()
    
    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        self.state('normal')
        self.fullscreen = False
        
    def toggle_fullscreen(self, event=None):
        """Toggle between fullscreen and windowed mode"""
        if self.fullscreen:
            self.state('normal')
            self.fullscreen = False
        else:
            self.state('zoomed')
            self.fullscreen = True
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Title frame
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="WUMPUS WORLD - RANDOM AGENT", 
                               font=('Arial', 24, 'bold'))
        title_label.pack()
        
        help_label = ttk.Label(title_frame, text="Press F11 to toggle fullscreen | Press ESC to exit fullscreen", 
                              font=('Arial', 12))
        help_label.pack()
        
        # Game board canvas - centered
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(expand=True, pady=(0, 10))
        
        self.canvas = tk.Canvas(
            canvas_frame, 
            width=self.width * self.cell_size,
            height=self.height * self.cell_size,
            bg='white',
            relief='sunken',
            borderwidth=3
        )
        self.canvas.pack()
        
        # Control frame - larger buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=(10, 0))
        
        # Center the buttons
        button_container = ttk.Frame(control_frame)
        button_container.pack(expand=True)
        
        # Larger buttons with better styling
        button_style = {'width': 15, 'padding': (10, 5)}
        
        self.start_button = ttk.Button(button_container, text="START AGENT", 
                                      command=self.start_game, **button_style)
        self.start_button.pack(side='left', padx=10)
        
        self.stop_button = ttk.Button(button_container, text="STOP AGENT", 
                                     command=self.stop_game, state='disabled', **button_style)
        self.stop_button.pack(side='left', padx=10)
        
        self.step_button = ttk.Button(button_container, text="SINGLE STEP", 
                                     command=self.single_step, **button_style)
        self.step_button.pack(side='left', padx=10)
        
        self.reset_button = ttk.Button(button_container, text="RESET GAME", 
                                      command=self.reset_game, **button_style)
        self.reset_button.pack(side='left', padx=10)
        
        # Exit button
        self.exit_button = ttk.Button(button_container, text="EXIT", 
                                     command=self.quit, **button_style)
        self.exit_button.pack(side='right', padx=10)
        
        # Status frame - improved layout
        status_frame = ttk.LabelFrame(main_frame, text="GAME STATUS", padding=10)
        status_frame.pack(fill='x', pady=(10, 0))
        
        # Create two columns for status
        status_container = ttk.Frame(status_frame)
        status_container.pack(fill='x')
        
        left_status = ttk.Frame(status_container)
        left_status.pack(side='left', fill='both', expand=True, padx=(0, 20))
        
        right_status = ttk.Frame(status_container)
        right_status.pack(side='right', fill='both', expand=True)
        
        # Status labels with larger fonts
        status_font = ('Arial', 14, 'bold')
        
        self.status_label = ttk.Label(left_status, text="Game Ready - Click START AGENT to begin", 
                                     font=status_font, foreground='blue')
        self.status_label.pack(anchor='w', pady=2)
        
        self.position_label = ttk.Label(left_status, text=f"Agent Position: ({self.agent.x}, {self.agent.y})", 
                                       font=status_font)
        self.position_label.pack(anchor='w', pady=2)
        
        self.direction_label = ttk.Label(left_status, text=f"Agent Direction: {self.agent.dir}", 
                                        font=status_font)
        self.direction_label.pack(anchor='w', pady=2)
        
        self.score_label = ttk.Label(right_status, text=f"Score: {self.agent.score}", 
                                    font=status_font, foreground='green')
        self.score_label.pack(anchor='w', pady=2)
        
        self.steps_label = ttk.Label(right_status, text=f"Steps: {self.steps}", 
                                    font=status_font)
        self.steps_label.pack(anchor='w', pady=2)
        
        # Percepts frame - improved
        percepts_frame = ttk.LabelFrame(main_frame, text="CURRENT PERCEPTS", padding=10)
        percepts_frame.pack(fill='x', pady=(10, 0))
        
        self.percepts_label = ttk.Label(percepts_frame, text="No percepts yet", 
                                       font=('Arial', 16, 'bold'), foreground='red')
        self.percepts_label.pack(pady=5)
        
        # Draw initial board
        self.draw_board()
        self.update_display()
    
    def draw_board(self):
        self.canvas.delete("all")
        
        # Draw grid
        for i in range(self.width + 1):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.height * self.cell_size, fill='gray')
        
        for i in range(self.height + 1):
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.width * self.cell_size, y, fill='gray')
        
        # Draw game elements from environment
        self.draw_environment_elements()
        self.draw_agent()
    
    def draw_environment_elements(self):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.env.grid[y][x]
                
                # Draw visited cells
                if cell.visited:
                    x1 = x * self.cell_size + 2
                    y1 = y * self.cell_size + 2
                    x2 = (x + 1) * self.cell_size - 2
                    y2 = (y + 1) * self.cell_size - 2
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='lightblue', outline='blue', tags='visited')
                
                # Draw wumpus
                if cell.has_wumpus:
                    x1 = x * self.cell_size + 5
                    y1 = y * self.cell_size + 5
                    x2 = (x + 1) * self.cell_size - 5
                    y2 = (y + 1) * self.cell_size - 5
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='red', outline='darkred', width=2, tags='wumpus')
                    self.canvas.create_text(x * self.cell_size + self.cell_size//2,
                                          y * self.cell_size + self.cell_size//2,
                                          text='W', fill='white', font=('Arial', 16, 'bold'), tags='wumpus')
                
                # Draw pits
                if cell.has_pit:
                    x1 = x * self.cell_size + 20
                    y1 = y * self.cell_size + 20
                    x2 = (x + 1) * self.cell_size - 20
                    y2 = (y + 1) * self.cell_size - 20
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='black', outline='gray', width=2, tags='pit')
                    self.canvas.create_text(x * self.cell_size + self.cell_size//2,
                                          y * self.cell_size + self.cell_size//2,
                                          text='P', fill='white', font=('Arial', 12, 'bold'), tags='pit')
                
                # Draw gold
                if cell.has_gold:
                    x1 = x * self.cell_size + 15
                    y1 = y * self.cell_size + 15
                    x2 = (x + 1) * self.cell_size - 15
                    y2 = (y + 1) * self.cell_size - 15
                    self.canvas.create_oval(x1, y1, x2, y2, fill='gold', outline='orange', width=2, tags='gold')
                    self.canvas.create_text(x * self.cell_size + self.cell_size//2,
                                          y * self.cell_size + self.cell_size//2,
                                          text='G', fill='black', font=('Arial', 12, 'bold'), tags='gold')
    
    def draw_agent(self):
        x, y = self.agent.x, self.agent.y
        x1 = x * self.cell_size + 10
        y1 = y * self.cell_size + 10
        x2 = (x + 1) * self.cell_size - 10
        y2 = (y + 1) * self.cell_size - 10
        
        # Agent color based on status
        color = 'blue' if self.agent.alive else 'red'
        if self.agent.has_gold:
            color = 'green'
            
        self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline='darkblue', width=2, tags='agent')
        
        # Direction arrow
        center_x = x * self.cell_size + self.cell_size//2
        center_y = y * self.cell_size + self.cell_size//2
        
        arrow_length = 15
        if self.agent.dir == 'N':
            end_x, end_y = center_x, center_y - arrow_length
        elif self.agent.dir == 'E':
            end_x, end_y = center_x + arrow_length, center_y
        elif self.agent.dir == 'S':
            end_x, end_y = center_x, center_y + arrow_length
        else:  # W
            end_x, end_y = center_x - arrow_length, center_y
            
        self.canvas.create_line(center_x, center_y, end_x, end_y, 
                              fill='white', width=3, arrow=tk.LAST, tags='agent')
    
    def update_display(self):
        # Update status labels
        self.position_label.config(text=f"Agent Position: ({self.agent.x}, {self.agent.y})")
        self.direction_label.config(text=f"Agent Direction: {self.agent.dir}")
        self.score_label.config(text=f"Score: {self.agent.score}")
        self.steps_label.config(text=f"Steps: {self.steps}")
        
        # Update percepts
        percepts = self.env.get_percepts(self.agent.x, self.agent.y)
        percept_text = []
        if percepts['stench']:
            percept_text.append("Stench")
        if percepts['breeze']:
            percept_text.append("Breeze")
        if percepts['glitter']:
            percept_text.append("Glitter")
        if self.env.scream:
            percept_text.append("Scream")
            self.env.scream = False  # Reset scream after showing
            
        self.percepts_label.config(text=f"Percepts: {', '.join(percept_text) if percept_text else 'None'}")
    
    def single_step(self):
        if self.game_over or not self.agent.alive:
            return
            
        continue_game = self.agent.step()
        self.steps += 1
        
        if not continue_game or not self.agent.alive:
            self.game_over = True
            if not self.agent.alive:
                self.status_label.config(text="Game Over! Agent died!")
                messagebox.showwarning("Game Over", "Agent died!")
            elif self.agent.has_gold and (self.agent.x, self.agent.y) == (0, 0):
                self.status_label.config(text="Success! Agent climbed out with gold!")
                messagebox.showinfo("Success", f"Agent won! Final Score: {self.agent.score}")
            else:
                self.status_label.config(text="Game ended")
        
        if self.steps > 100:
            self.game_over = True
            self.status_label.config(text="Game Over! Too many steps!")
            messagebox.showwarning("Game Over", "Agent took too many steps!")
        
        self.draw_board()
        self.update_display()
    
    def start_game(self):
        if not self.game_over:
            self.game_running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.step_button.config(state='disabled')
            self.status_label.config(text="Agent is exploring...")
            self.run_agent()
    
    def stop_game(self):
        self.game_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.step_button.config(state='normal')
        self.status_label.config(text="Agent stopped")
    
    def reset_game(self):
        self.stop_game()
        self.env = Environment()
        self.agent = RandomAgent(self.env)
        self.game_over = False
        self.steps = 0
        self.status_label.config(text="Game Reset - Click Start Agent to begin")
        self.start_button.config(state='normal')
        self.step_button.config(state='normal')
        self.draw_board()
        self.update_display()
    
    def run_agent(self):
        if not self.game_running or self.game_over:
            return
            
        self.single_step()
        
        # Schedule next move if game is still running
        if self.game_running and not self.game_over and self.agent.alive:
            self.after(1000, self.run_agent)  # Move every second
        else:
            self.stop_game()

def main():
    app = GameBoardUI()
    app.mainloop()

if __name__ == "__main__":
    main()
