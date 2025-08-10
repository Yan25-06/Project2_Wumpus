import tkinter as tk
from tkinter import ttk, messagebox
import time
from ..core.environment import Environment
from ..agents.random_agent import RandomAgent
from ..agents.hybrid_agent import HybridAgent
class GameBoardUI(tk.Tk):
    def __init__(self, width=8, height=8):
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
        # Agent mode and board size variables
        self.agent_mode = "Random"  # Default to Random
        self.board_size = 8  # Default board size
        
        self.env = Environment(N=self.board_size)
        self.agent = RandomAgent(self.env)
        self.game_running = False
        self.game_over = False
        self.steps = 0
        self.moves_history = []  # Track all agent moves
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Title frame
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 10))
        
        # Create horizontal layout: board on left, controls on right
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(expand=True, fill='both', pady=(0, 10))
        
        # Left side - Game board
        board_frame = ttk.LabelFrame(content_frame, text="GAME BOARD", padding=10)
        board_frame.pack(side='left', fill='both', padx=(0, 10))  # Removed expand=True and fill='both'
        
        self.canvas = tk.Canvas(
            board_frame, 
            width=self.width * self.cell_size,
            height=self.height * self.cell_size,
            bg='white',
            relief='sunken',
            borderwidth=3
        )
        self.canvas.pack()
        
        # Right side - Controls and status
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side='right', fill='y', padx=(10, 0))
        
        # Control frame - improved layout for right panel
        control_frame = ttk.LabelFrame(right_panel, text="CONTROLS", padding=10)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Button styling for vertical layout
        button_style = {'width': 20, 'padding': (10, 5)}
        
        self.start_button = ttk.Button(control_frame, text="START AGENT", 
                                      command=self.start_game, **button_style)
        self.start_button.pack(pady=2)
        
        self.stop_button = ttk.Button(control_frame, text="STOP AGENT", 
                                     command=self.stop_game, state='disabled', **button_style)
        self.stop_button.pack(pady=2)
        
        self.reset_button = ttk.Button(control_frame, text="RESET GAME", 
                                      command=self.reset_game, **button_style)
        self.reset_button.pack(pady=2)
        
        # Agent mode selection button
        self.agent_button = ttk.Button(control_frame, text=f"AGENT: {self.agent_mode}", 
                                     command=self.toggle_agent_mode, **button_style)
        self.agent_button.pack(pady=2)
        
        # Board size selection button
        self.size_button = ttk.Button(control_frame, text=f"SIZE: {self.board_size}x{self.board_size}", 
                                    command=self.change_board_size, **button_style)
        self.size_button.pack(pady=2)
        
        # Compare agents button
        self.compare_button = ttk.Button(control_frame, text="COMPARE AGENTS", 
                                       command=self.compare_agents, **button_style)
        self.compare_button.pack(pady=2)
        
        # Exit button
        self.exit_button = ttk.Button(control_frame, text="EXIT", 
                                     command=self.quit, **button_style)
        self.exit_button.pack(pady=2)
        
        # Status frame - improved layout for right panel
        status_frame = ttk.LabelFrame(right_panel, text="GAME STATUS", padding=10)
        status_frame.pack(fill='x', pady=(10, 0))
        
        # Status labels with improved layout
        status_font = ('Arial', 12, 'bold')
        
        self.status_label = ttk.Label(status_frame, text="Game Ready - Click START AGENT to begin", 
                                     font=status_font, foreground='blue', wraplength=250)
        self.status_label.pack(pady=2)
        
        self.position_label = ttk.Label(status_frame, text=f"Agent Position: ({self.agent.x}, {self.agent.y})", 
                                       font=status_font)
        self.position_label.pack(pady=2)
        
        self.direction_label = ttk.Label(status_frame, text=f"Agent Direction: {self.agent.dir}", 
                                        font=status_font)
        self.direction_label.pack(pady=2)
        
        self.score_label = ttk.Label(status_frame, text=f"Score: {self.agent.score}", 
                                    font=status_font, foreground='green')
        self.score_label.pack(pady=2)
        
        self.steps_label = ttk.Label(status_frame, text=f"Steps: {self.steps}", 
                                    font=status_font)
        self.steps_label.pack(pady=2)
        
        # Moves history frame - show recent moves
        moves_frame = ttk.LabelFrame(right_panel, text="MOVES HISTORY", padding=10)
        moves_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Create scrollable text widget for moves history
        moves_container = ttk.Frame(moves_frame)
        moves_container.pack(fill='both', expand=True)
        
        # Scrollbar for moves history
        scrollbar = ttk.Scrollbar(moves_container)
        scrollbar.pack(side='right', fill='y')
        
        # Text widget for moves history
        self.moves_text = tk.Text(moves_container, height=10, width=30, 
                                 font=('Arial', 9), wrap='word',
                                 yscrollcommand=scrollbar.set)
        self.moves_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.moves_text.yview)
        
        # Draw initial board
        self.draw_board()
        self.update_display()
        
        # Add initial position to moves history
        initial_percepts = self.env.get_percepts(self.agent.x, self.agent.y)
        self.add_move_to_history("Start", (self.agent.x, self.agent.y), self.agent.dir, "GAME BEGIN")
    
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
                # Convert to canvas coordinates (flip Y-axis so (0,0) is bottom-left)
                canvas_y = (self.height - 1 - y)
                
                # Draw visited cells
                if self.env.is_visited(x, y):
                    margin = max(1, self.cell_size // 50)  # Dynamic margin for visited cells
                    x1 = x * self.cell_size + margin
                    y1 = canvas_y * self.cell_size + margin
                    x2 = (x + 1) * self.cell_size - margin
                    y2 = (canvas_y + 1) * self.cell_size - margin
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='lightblue', outline='blue', tags='visited')
                
                # Draw percepts on ALL cells (not just visited ones)
                if not self.env.has_gold(x, y) and not self.env.has_wumpus(x, y) and not self.env.has_pit(x, y):
                    self.draw_percepts_on_cell(x, canvas_y)
                
                # Draw wumpus
                if self.env.has_wumpus(x, y):
                    margin = max(3, self.cell_size // 20)  # Dynamic margin (3-6px depending on cell size)
                    x1 = x * self.cell_size + margin
                    y1 = canvas_y * self.cell_size + margin
                    x2 = (x + 1) * self.cell_size - margin
                    y2 = (canvas_y + 1) * self.cell_size - margin
                    border_width = max(1, self.cell_size // 40)  # Dynamic border width
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='red', outline='darkred', width=border_width, tags='wumpus')
                    font_size = max(8, self.cell_size // 6)  # Dynamic font size
                    self.canvas.create_text(x * self.cell_size + self.cell_size//2,
                                          canvas_y * self.cell_size + self.cell_size//2,
                                          text='W', fill='white', font=('Arial', font_size, 'bold'), tags='wumpus')
                
                # Draw pits
                if self.env.has_pit(x, y):
                    margin = max(15, self.cell_size // 4)  # Dynamic margin (scales with cell size)
                    x1 = x * self.cell_size + margin
                    y1 = canvas_y * self.cell_size + margin
                    x2 = (x + 1) * self.cell_size - margin
                    y2 = (canvas_y + 1) * self.cell_size - margin
                    border_width = max(1, self.cell_size // 40)  # Dynamic border width
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='black', outline='gray', width=border_width, tags='pit')
                    font_size = max(6, self.cell_size // 8)  # Dynamic font size for pit text
                    self.canvas.create_text(x * self.cell_size + self.cell_size//2,
                                          canvas_y * self.cell_size + self.cell_size//2,
                                          text='P', fill='white', font=('Arial', font_size, 'bold'), tags='pit')
                
                # Draw gold
                if self.env.has_gold(x, y):
                    margin = max(10, self.cell_size // 6)  # Dynamic margin for gold
                    x1 = x * self.cell_size + margin
                    y1 = canvas_y * self.cell_size + margin
                    x2 = (x + 1) * self.cell_size - margin
                    y2 = (canvas_y + 1) * self.cell_size - margin
                    border_width = max(1, self.cell_size // 40)  # Dynamic border width
                    self.canvas.create_oval(x1, y1, x2, y2, fill='gold', outline='orange', width=border_width, tags='gold')
                    font_size = max(6, self.cell_size // 8)  # Dynamic font size for gold text
                    self.canvas.create_text(x * self.cell_size + self.cell_size//2,
                                          canvas_y * self.cell_size + self.cell_size//2,
                                          text='Gold', fill='black', font=('Arial', font_size, 'bold'), tags='gold')
    
    def draw_percepts_on_cell(self, x, canvas_y):
        """Draw percept indicators on all cells"""
        # Convert canvas_y back to world y for percept calculation
        world_y = (self.height - 1 - canvas_y)
        
        # Calculate percepts directly for this cell
        percepts = {
            'stench': False,
            'breeze': False,
            'glitter': False
        }
        
        # Check for stench (adjacent to wumpus)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            adj_x, adj_y = x + dx, world_y + dy
            if 0 <= adj_x < self.width and 0 <= adj_y < self.height:
                if self.env.has_wumpus(adj_x, adj_y):
                    percepts['stench'] = True
                    break
        
        # Check for breeze (adjacent to pit)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            adj_x, adj_y = x + dx, world_y + dy
            if 0 <= adj_x < self.width and 0 <= adj_y < self.height:
                if self.env.has_pit(adj_x, adj_y):
                    percepts['breeze'] = True
                    break
        
        # Check for glitter (gold in same cell)
        if self.env.has_gold(x, world_y):
            percepts['glitter'] = True
        
        # Calculate center position for percept indicators (using canvas coordinates)
        cell_x = x * self.cell_size
        cell_y = canvas_y * self.cell_size
        center_x = cell_x + self.cell_size // 2
        center_y = cell_y + self.cell_size // 2
        
        # Collect percepts and arrange them vertically to avoid overlap
        percept_list = []
        if percepts['stench']:
            percept_list.append(('S', 'green', 'darkgreen', 'white'))
        if percepts['breeze']:
            percept_list.append(('B', 'blue', 'darkblue', 'white'))
        if percepts['glitter']:
            percept_list.append(('Glitter', 'yellow', 'orange', 'black'))
        
        # Draw all percepts vertically arranged
        if len(percept_list) == 1:
            # Single percept - center it
            text, fill_color, outline_color, text_color = percept_list[0]
            radius = max(15, self.cell_size // 15)  # Dynamic radius based on cell size
            self.canvas.create_oval(center_x - radius, center_y - radius, 
                                  center_x + radius, center_y + radius, 
                                  fill=fill_color, outline=outline_color, width=2, tags='percept')
            font_size = max(7, self.cell_size // 15)  # Dynamic font size for percepts
            self.canvas.create_text(center_x, center_y, text=text, 
                                  fill=text_color, font=('Arial', font_size, 'bold'), tags='percept')
        
        elif len(percept_list) == 2:
            # Two percepts - arrange vertically
            for i, (text, fill_color, outline_color, text_color) in enumerate(percept_list):
                radius = max(8, self.cell_size // 10)  # Slightly smaller for multiple percepts
                y_offset = (-radius*0.8) if i == 0 else (radius*0.8)  # Dynamic spacing
                self.canvas.create_oval(center_x - radius, center_y + y_offset - radius, 
                                      center_x + radius, center_y + y_offset + radius, 
                                      fill=fill_color, outline=outline_color, width=2, tags='percept')
                font_size = max(4, self.cell_size // 15)  # Smaller font for multiple percepts
                self.canvas.create_text(center_x, center_y + y_offset, text=text, 
                                      fill=text_color, font=('Arial', font_size, 'bold'), tags='percept')
        
        elif len(percept_list) == 3:
            # Three percepts - arrange in triangle pattern
            radius = max(6, self.cell_size // 12)  # Even smaller for three percepts
            spacing = radius * 1.2  # Dynamic spacing based on radius
            positions = [(-spacing, -spacing*0.6), (spacing, -spacing*0.6), (0, spacing)]  # top-left, top-right, bottom
            for i, (text, fill_color, outline_color, text_color) in enumerate(percept_list):
                x_offset, y_offset = positions[i]
                self.canvas.create_oval(center_x + x_offset - radius, center_y + y_offset - radius, 
                                      center_x + x_offset + radius, center_y + y_offset + radius, 
                                      fill=fill_color, outline=outline_color, width=2, tags='percept')
                font_size = max(3, self.cell_size // 18)  # Smallest font for three percepts
                self.canvas.create_text(center_x + x_offset, center_y + y_offset, text=text, 
                                      fill=text_color, font=('Arial', font_size, 'bold'), tags='percept')
    
    def add_move_to_history(self, action, position, direction, result=""):
        """Add a move to the history display"""
        move_num = len(self.moves_history) + 1
        
        move_entry = {
            'number': move_num,
            'action': action,
            'position': position,
            'direction': direction,
            'result': result
        }
        
        self.moves_history.append(move_entry)
        
        # Format move for display
        move_text = f"{move_num:2d}. {action:12s} -> ({position[0]},{position[1]})" 
        if result:
            move_text += f" | {result}"
        move_text += "\n"
        
        # Add to text widget
        self.moves_text.insert(tk.END, move_text)
        self.moves_text.see(tk.END)  # Scroll to bottom
        
        # Limit history to last 50 moves to prevent memory issues
        if len(self.moves_history) > 50:
            self.moves_history = self.moves_history[-50:]
            # Clear and reload text widget
            self.moves_text.delete(1.0, tk.END)
            for move in self.moves_history:
                move_text = f"{move['number']:2d}. {move['action']:12s} -> ({move['position'][0]},{move['position'][1]}) {move['direction']} | {move['percepts']}"
                if move['result']:
                    move_text += f" | {move['result']}"
                move_text += "\n"
                self.moves_text.insert(tk.END, move_text)
    
    def draw_agent(self):
        x, y = self.agent.x, self.agent.y
        # Convert to canvas coordinates (flip Y-axis so (0,0) is bottom-left)
        canvas_y = (self.height - 1 - y)
        
        margin = max(8, self.cell_size // 12)  # Dynamic margin for agent
        x1 = x * self.cell_size + margin
        y1 = canvas_y * self.cell_size + margin
        x2 = (x + 1) * self.cell_size - margin
        y2 = (canvas_y + 1) * self.cell_size - margin
        
        # Agent color based on status
        color = 'blue' if self.agent.alive else 'red'
        if self.agent.has_gold:
            color = 'green'
        
        border_width = max(1, self.cell_size // 40)  # Dynamic border width
        self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline='darkblue', width=border_width, tags='agent')
        
        # Direction arrow
        center_x = x * self.cell_size + self.cell_size//2
        center_y = canvas_y * self.cell_size + self.cell_size//2
        
        arrow_length = max(8, self.cell_size // 6)  # Dynamic arrow length
        arrow_width = max(2, self.cell_size // 30)  # Dynamic arrow width
        if self.agent.dir == 'N':
            end_x, end_y = center_x, center_y - arrow_length
        elif self.agent.dir == 'E':
            end_x, end_y = center_x + arrow_length, center_y
        elif self.agent.dir == 'S':
            end_x, end_y = center_x, center_y + arrow_length
        else:  # W
            end_x, end_y = center_x - arrow_length, center_y
            
        self.canvas.create_line(center_x, center_y, end_x, end_y, 
                              fill='white', width=arrow_width, arrow=tk.LAST, tags='agent')
    
    def update_display(self):
        # Update status labels
        self.position_label.config(text=f"Agent Position: ({self.agent.x}, {self.agent.y})")
        self.direction_label.config(text=f"Agent Direction: {self.agent.dir}")
        self.score_label.config(text=f"Score: {self.agent.score}")
        self.steps_label.config(text=f"Steps: {self.steps}")
        
        # Reset scream if it was triggered
        if self.env.get_scream():
            self.env.reset_scream()  # Reset scream after checking
    
    def single_step(self):
        if self.game_over or not self.agent.alive:
            return
        
        # Record state before action
        prev_pos = (self.agent.x, self.agent.y)
        prev_dir = self.agent.dir
        prev_score = self.agent.score
        prev_has_gold = self.agent.has_gold
        prev_can_shoot = self.agent.can_shoot
        
        # Get current percepts before action
        current_percepts = self.env.get_percepts(self.agent.x, self.agent.y)
        
        # Capture stdout to get agent's print messages
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        try:
            # Execute agent step
            continue_game = self.agent.step()
            self.steps += 1
        finally:
            # Restore stdout
            sys.stdout = old_stdout
        
        # Get the captured output (agent's print messages)
        agent_messages = captured_output.getvalue().strip()
        
        # Determine what action was taken by comparing states
        new_pos = (self.agent.x, self.agent.y)
        new_dir = self.agent.dir
        new_score = self.agent.score
        new_has_gold = self.agent.has_gold
        
        # Use agent's printed message as the action, or fall back to detecting action
        if agent_messages:
            action_taken = agent_messages
        else:
            # Fallback action detection
            if new_pos != prev_pos:
                action_taken = f"Agent moved to ({new_pos[0]}, {new_pos[1]}) facing {new_dir}"
                if not self.agent.alive:
                    action_taken += " - Agent died!"
            elif new_dir != prev_dir:
                dirs = ['N', 'E', 'S', 'W']
                prev_idx = dirs.index(prev_dir)
                new_idx = dirs.index(new_dir)
                direction_word = 'right' if (new_idx - prev_idx) % 4 == 1 else 'left'
                action_taken = f"Agent turned {direction_word} to {new_dir}"
            elif new_has_gold and not prev_has_gold:
                action_taken = "Agent grabbed the gold!"
            elif new_score == prev_score - 10:
                action_taken = "Agent shot and " + ("killed the Wumpus!" if self.env.get_scream() else "missed.")
            elif not continue_game and (self.agent.x, self.agent.y) == (0, 0):
                action_taken = f"Agent climbed out {'with' if self.agent.has_gold else 'without'} the gold!"
            else:
                action_taken = "Unknown action"
        
        result = ""
        if not self.agent.alive:
            result = "DIED!"
        elif self.agent.has_gold and not prev_has_gold:
            result = "GOT GOLD!"
        elif self.env.get_scream():
            result = "HIT WUMPUS!"
        
        # Add move to history with agent's exact message
        self.add_move_to_history(action_taken, new_pos, new_dir, result)
        
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
            self.status_label.config(text="Agent is exploring...")
            self.run_agent()
    
    def stop_game(self):
        self.game_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="Agent stopped")
    
    def reset_game(self):
        self.stop_game()
        self.env = Environment(N=self.board_size)
        # Create agent based on current mode
        if self.agent_mode == "Random":
            self.agent = RandomAgent(self.env)
        else:  # Hybrid
            self.agent = HybridAgent(self.env)
        self.game_over = False
        self.steps = 0
        self.moves_history = []  # Clear moves history
        self.moves_text.delete(1.0, tk.END)  # Clear moves display
        self.status_label.config(text="Game Reset - Click Start Agent to begin")
        self.start_button.config(state='normal')
        self.draw_board()
        self.update_display()
    
    def toggle_agent_mode(self):
        """Toggle between Random and Hybrid agent modes"""
        if self.game_running:
            messagebox.showwarning("Cannot Change", "Stop the game before changing agent mode!")
            return
            
        self.agent_mode = "Hybrid" if self.agent_mode == "Random" else "Random"
        self.agent_button.config(text=f"AGENT: {self.agent_mode}")
        
        # Recreate agent with new mode
        if self.agent_mode == "Random":
            self.agent = RandomAgent(self.env)
        else:  # Hybrid
            self.agent = HybridAgent(self.env)
        
        self.update_display()
        messagebox.showinfo("Agent Changed", f"Agent mode changed to: {self.agent_mode}")
    
    def change_board_size(self):
        """Change the board size"""
        if self.game_running:
            messagebox.showwarning("Cannot Change", "Stop the game before changing board size!")
            return
            
        # Show size selection dialog
        sizes = [4, 6, 8, 10, 12, 16]
        size_window = tk.Toplevel(self)
        size_window.title("Select Board Size")
        size_window.geometry("400x350")
        size_window.resizable(False, False)
        
        # Center the dialog
        size_window.transient(self)
        size_window.grab_set()
        
        # Main container
        main_container = ttk.Frame(size_window, padding=15)
        main_container.pack(fill='both', expand=True)
        
        ttk.Label(main_container, text="Choose Board Size:", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        selected_size = tk.IntVar(value=self.board_size)
        
        # Radio buttons frame
        radio_frame = ttk.Frame(main_container)
        radio_frame.pack(pady=10)
        
        for size in sizes:
            ttk.Radiobutton(radio_frame, text=f"{size}x{size} Grid", 
                          variable=selected_size, value=size,
                          style='TRadiobutton').pack(pady=5, anchor='w')
        
        def apply_size():
            new_size = selected_size.get()
            if new_size != self.board_size:
                self.board_size = new_size
                self.width = new_size
                self.height = new_size
                self.size_button.config(text=f"SIZE: {self.board_size}x{self.board_size}")
                
                # Recalculate cell size based on new board size
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                available_width = screen_width - 600  # Reserve space for right panel
                available_height = screen_height - 250  # Leave space for title and margins
                
                # Calculate optimal cell size for new board size
                max_cell_width = available_width // self.width
                max_cell_height = available_height // self.height
                self.cell_size = min(max_cell_width, max_cell_height, 120)  # Cap at 120px for very small boards
                
                print(f"New board size: {new_size}x{new_size}, Cell size: {self.cell_size}px")
                
                # Recreate environment and agent with new size
                self.env = Environment(N=new_size)
                if self.agent_mode == "Random":
                    self.agent = RandomAgent(self.env)
                else:  # Hybrid
                    self.agent = HybridAgent(self.env)
                
                # Update canvas size with new cell size
                self.canvas.config(width=self.width * self.cell_size, 
                                 height=self.height * self.cell_size)
                
                # Reset game state
                self.game_over = False
                self.steps = 0
                self.moves_history = []
                self.moves_text.delete(1.0, tk.END)
                
                self.draw_board()
                self.update_display()
                
                messagebox.showinfo("Board Size Changed", f"Board size changed to: {new_size}x{new_size}\nCell size: {self.cell_size}px")
            
            size_window.destroy()
        
        # Button frame
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=(30, 0))
        
        # Style the buttons
        apply_btn = ttk.Button(button_frame, text="Apply Changes", command=apply_size)
        apply_btn.pack(side='left', padx=(0, 10), ipadx=20, ipady=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=size_window.destroy)
        cancel_btn.pack(side='left', padx=(10, 0), ipadx=20, ipady=5)
    
    def compare_agents(self):
        """Compare Random and Hybrid agents on the same map"""
        if self.game_running:
            messagebox.showwarning("Cannot Compare", "Stop the current game before comparing agents!")
            return
        
        # Store current environment state to restore later
        original_env = self.env
        
        # Create comparison window
        compare_window = tk.Toplevel(self)
        compare_window.title("Agent Comparison Results")
        compare_window.geometry("600x500")
        compare_window.resizable(True, True)
        compare_window.transient(self)
        compare_window.grab_set()
        
        # Main container
        main_container = ttk.Frame(compare_window, padding=15)
        main_container.pack(fill='both', expand=True)
        
        ttk.Label(main_container, text="Agent Performance Comparison", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 15))
        
        ttk.Label(main_container, text="Running both agents on the same map...", 
                 font=('Arial', 12)).pack(pady=(0, 10))
        
        # Progress bar
        progress = ttk.Progressbar(main_container, mode='indeterminate')
        progress.pack(fill='x', pady=(0, 20))
        progress.start()
        
        # Results frame
        results_frame = ttk.Frame(main_container)
        results_frame.pack(fill='both', expand=True)
        
        # Create scrollable text widget for results
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill='both', expand=True)
        
        scrollbar_compare = ttk.Scrollbar(text_frame)
        scrollbar_compare.pack(side='right', fill='y')
        
        results_text = tk.Text(text_frame, font=('Courier', 10), wrap='word',
                              yscrollcommand=scrollbar_compare.set)
        results_text.pack(side='left', fill='both', expand=True)
        scrollbar_compare.config(command=results_text.yview)
        
        def run_comparison():
            try:
                # Save the current map configuration
                saved_wumpus_pos = None
                saved_pit_positions = []
                saved_gold_pos = None
                
                # Find current positions
                for y in range(self.height):
                    for x in range(self.width):
                        if self.env.has_wumpus(x, y):
                            saved_wumpus_pos = (x, y)
                        if self.env.has_pit(x, y):
                            saved_pit_positions.append((x, y))
                        if self.env.has_gold(x, y):
                            saved_gold_pos = (x, y)
                
                results_text.insert(tk.END, "=== AGENT COMPARISON RESULTS ===\n\n")
                results_text.insert(tk.END, f"Board Size: {self.board_size}x{self.board_size}\n")
                results_text.insert(tk.END, f"Wumpus Position: {saved_wumpus_pos}\n")
                results_text.insert(tk.END, f"Pit Positions: {saved_pit_positions}\n") 
                results_text.insert(tk.END, f"Gold Position: {saved_gold_pos}\n\n")
                
                # Test both agents
                agent_results = {}
                
                for agent_name in ["Random", "Hybrid"]:
                    results_text.insert(tk.END, f"--- Testing {agent_name} Agent ---\n")
                    results_text.update()
                    
                    # Create new environment with same configuration
                    test_env = Environment(N=self.board_size)
                    
                    # Restore the exact same map configuration
                    if saved_wumpus_pos:
                        test_env.wumpus_location = saved_wumpus_pos
                    if saved_pit_positions:
                        test_env.pit_locations = saved_pit_positions.copy()
                    if saved_gold_pos:
                        test_env.gold_location = saved_gold_pos
                    
                    # Create agent
                    if agent_name == "Random":
                        test_agent = RandomAgent(test_env)
                    else:
                        test_agent = HybridAgent(test_env)
                    
                    # Run agent with step limit
                    steps = 0
                    max_steps = 100
                    game_outcome = "Unknown"
                    
                    while steps < max_steps and test_agent.alive:
                        continue_game = test_agent.step()
                        steps += 1
                        
                        if not continue_game:
                            if test_agent.has_gold and (test_agent.x, test_agent.y) == (0, 0):
                                game_outcome = "Won with Gold"
                            elif (test_agent.x, test_agent.y) == (0, 0):
                                game_outcome = "Climbed out without Gold"
                            else:
                                game_outcome = "Quit Game"
                            break
                        
                        if not test_agent.alive:
                            game_outcome = "Died"
                            break
                    
                    if steps >= max_steps:
                        game_outcome = "Timeout (100+ steps)"
                    
                    # Store results
                    agent_results[agent_name] = {
                        'steps': steps,
                        'score': test_agent.score,
                        'outcome': game_outcome,
                        'has_gold': test_agent.has_gold,
                        'alive': test_agent.alive
                    }
                    
                    # Display results
                    results_text.insert(tk.END, f"  Steps: {steps}\n")
                    results_text.insert(tk.END, f"  Final Score: {test_agent.score}\n")
                    results_text.insert(tk.END, f"  Outcome: {game_outcome}\n")
                    results_text.insert(tk.END, f"  Has Gold: {test_agent.has_gold}\n")
                    results_text.insert(tk.END, f"  Alive: {test_agent.alive}\n\n")
                    results_text.update()
                
                # Summary comparison
                results_text.insert(tk.END, "=== COMPARISON SUMMARY ===\n\n")
                
                random_result = agent_results["Random"]
                hybrid_result = agent_results["Hybrid"]
                
                # Determine winner
                winner = None
                if random_result['score'] > hybrid_result['score']:
                    winner = "Random"
                elif hybrid_result['score'] > random_result['score']:
                    winner = "Hybrid"
                else:
                    winner = "Tie"
                
                results_text.insert(tk.END, f"Winner: {winner} Agent\n\n")
                
                # Detailed comparison
                results_text.insert(tk.END, "Score Comparison:\n")
                results_text.insert(tk.END, f"  Random Agent: {random_result['score']}\n")
                results_text.insert(tk.END, f"  Hybrid Agent: {hybrid_result['score']}\n\n")
                
                results_text.insert(tk.END, "Steps Comparison:\n")
                results_text.insert(tk.END, f"  Random Agent: {random_result['steps']}\n")
                results_text.insert(tk.END, f"  Hybrid Agent: {hybrid_result['steps']}\n\n")
                
                results_text.insert(tk.END, "Outcome Comparison:\n")
                results_text.insert(tk.END, f"  Random Agent: {random_result['outcome']}\n")
                results_text.insert(tk.END, f"  Hybrid Agent: {hybrid_result['outcome']}\n\n")
                
                # Efficiency analysis
                if winner != "Tie":
                    winning_agent = agent_results[winner]
                    losing_agent = agent_results["Random" if winner == "Hybrid" else "Hybrid"]
                    
                    score_diff = winning_agent['score'] - losing_agent['score']
                    step_diff = winning_agent['steps'] - losing_agent['steps']
                    
                    results_text.insert(tk.END, f"Performance Analysis:\n")
                    results_text.insert(tk.END, f"  {winner} agent scored {score_diff} points better\n")
                    
                    if step_diff < 0:
                        results_text.insert(tk.END, f"  {winner} agent was {abs(step_diff)} steps more efficient\n")
                    elif step_diff > 0:
                        results_text.insert(tk.END, f"  {winner} agent took {step_diff} more steps\n")
                    else:
                        results_text.insert(tk.END, f"  Both agents took the same number of steps\n")
                
                progress.stop()
                progress.pack_forget()
                
                # Close button
                close_frame = ttk.Frame(main_container)
                close_frame.pack(pady=(20, 0))
                
                ttk.Button(close_frame, text="Close", 
                          command=compare_window.destroy).pack()
                
            except Exception as e:
                progress.stop()
                results_text.insert(tk.END, f"Error during comparison: {str(e)}\n")
                messagebox.showerror("Comparison Error", f"An error occurred: {str(e)}")
        
        # Run comparison in a separate thread to avoid blocking UI
        compare_window.after(100, run_comparison)
    
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
