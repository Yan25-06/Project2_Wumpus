import tkinter as tk
from tkinter import ttk


class SetupUI:
    """Handles UI setup and layout for the Wumpus World game"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Title frame
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 10))
        
        # Create horizontal layout: board on left, controls on right
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(expand=True, fill='both', pady=(0, 10))
        
        # Setup board frame
        self.setup_board_frame(content_frame)
        
        # Setup right panel
        self.setup_right_panel(content_frame)
        
        return main_frame
    
    def setup_board_frame(self, parent_frame):
        """Setup the game board frame"""
        # Left side - Game board
        board_frame = ttk.LabelFrame(parent_frame, text="GAME BOARD", padding=10)
        board_frame.pack(side='left', fill='both', padx=(0, 10))
        
        # Store reference to board frame for use in other parts of the application
        self.parent.left_frame = board_frame
        
        self.parent.canvas = tk.Canvas(
            board_frame, 
            width=self.parent.width * self.parent.cell_size,
            height=self.parent.height * self.parent.cell_size,
            bg='white',
            relief='sunken',
            borderwidth=3
        )
        self.parent.canvas.pack()
    
    def setup_right_panel(self, parent_frame):
        """Setup the right panel with controls and status"""
        # Right side - Controls and status
        right_panel = ttk.Frame(parent_frame)
        right_panel.pack(side='right', fill='y', padx=(10, 0))
        
        # Setup control frame
        self.setup_control_frame(right_panel)
        
        # Setup status frame
        self.setup_status_frame(right_panel)
        
        # Setup moves history frame
        self.setup_moves_history_frame(right_panel)
    
    def setup_control_frame(self, parent_panel):
        """Setup the control buttons frame"""
        # Control frame - improved layout for right panel
        control_frame = ttk.LabelFrame(parent_panel, text="CONTROLS", padding=10)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Button styling for vertical layout
        button_style = {'width': 20, 'padding': (10, 5)}
        
        self.parent.start_button = ttk.Button(control_frame, text="START AGENT", 
                                      command=self.parent.start_game, **button_style)
        self.parent.start_button.pack(pady=2)
        
        self.parent.stop_button = ttk.Button(control_frame, text="STOP AGENT", 
                                     command=self.parent.stop_game, state='disabled', **button_style)
        self.parent.stop_button.pack(pady=2)
        
        self.parent.reset_button = ttk.Button(control_frame, text="RESET GAME", 
                                      command=self.parent.reset_game, **button_style)
        self.parent.reset_button.pack(pady=2)
        
        # Game settings button (agent type, board size, pit probability, wumpus count)
        self.parent.size_button = ttk.Button(control_frame, text="SETTINGS", 
                                    command=self.parent.button_functions.change_board_size, **button_style)
        self.parent.size_button.pack(pady=2)
        
        # Compare agents button
        self.parent.compare_button = ttk.Button(control_frame, text="COMPARE AGENTS", 
                                       command=self.parent.compare_agents, **button_style)
        self.parent.compare_button.pack(pady=2)
        
        # Exit button
        self.parent.exit_button = ttk.Button(control_frame, text="EXIT", 
                                     command=self.parent.quit, **button_style)
        self.parent.exit_button.pack(pady=2)
    
    def setup_status_frame(self, parent_panel):
        """Setup the status display frame"""
        # Status frame - improved layout for right panel
        status_frame = ttk.LabelFrame(parent_panel, text="GAME STATUS", padding=10)
        status_frame.pack(fill='x', pady=(10, 0))
        
        # Status labels with improved layout
        status_font = ('Arial', 12, 'bold')
        
        self.parent.status_label = ttk.Label(status_frame, text="Game Ready - Click START AGENT to begin", 
                                     font=status_font, foreground='blue', wraplength=250)
        self.parent.status_label.pack(pady=2)
        
        self.parent.position_label = ttk.Label(status_frame, text=f"Agent Position: ({self.parent.agent.x}, {self.parent.agent.y})", 
                                       font=status_font)
        self.parent.position_label.pack(pady=2)
        
        self.parent.direction_label = ttk.Label(status_frame, text=f"Agent Direction: {self.parent.agent.dir}", 
                                        font=status_font)
        self.parent.direction_label.pack(pady=2)
        
        self.parent.score_label = ttk.Label(status_frame, text=f"Score: {self.parent.agent.score}", 
                                    font=status_font, foreground='green')
        self.parent.score_label.pack(pady=2)
        
        self.parent.steps_label = ttk.Label(status_frame, text=f"Steps: {self.parent.agent.steps}", 
                                    font=status_font)
        self.parent.steps_label.pack(pady=2)
    
    def setup_moves_history_frame(self, parent_panel):
        """Setup the moves history frame"""
        # Moves history frame - show recent moves
        moves_frame = ttk.LabelFrame(parent_panel, text="MOVES HISTORY", padding=10)
        moves_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Create scrollable text widget for moves history
        moves_container = ttk.Frame(moves_frame)
        moves_container.pack(fill='both', expand=True)
        
        # Scrollbar for moves history
        scrollbar = ttk.Scrollbar(moves_container)
        scrollbar.pack(side='right', fill='y')
        
        # Text widget for moves history
        self.parent.moves_text = tk.Text(moves_container, height=10, width=30, 
                                 font=('Arial', 9), wrap='word',
                                 yscrollcommand=scrollbar.set)
        self.parent.moves_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.parent.moves_text.yview)
