import tkinter as tk


class DrawUI:
    """Handles all drawing operations for the Wumpus World game board"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def draw_board(self):
        """Draw the complete game board"""
        self.parent.canvas.delete("all")
        
        # Draw grid
        for i in range(self.parent.width + 1):
            x = i * self.parent.cell_size
            self.parent.canvas.create_line(x, 0, x, self.parent.height * self.parent.cell_size, fill='gray')
        
        for i in range(self.parent.height + 1):
            y = i * self.parent.cell_size
            self.parent.canvas.create_line(0, y, self.parent.width * self.parent.cell_size, y, fill='gray')
        
        # Draw game elements from environment
        self.draw_environment_elements()
        self.draw_agent()
    
    def draw_environment_elements(self):
        """Draw all environment elements (wumpus, pits, gold, visited cells, percepts)"""
        for y in range(self.parent.height):
            for x in range(self.parent.width):
                # Convert to canvas coordinates (flip Y-axis so (0,0) is bottom-left)
                canvas_y = (self.parent.height - 1 - y)
                
                # Draw visited cells
                if self.parent.env.is_visited(x, y):
                    margin = max(1, self.parent.cell_size // 50)  # Dynamic margin for visited cells
                    x1 = x * self.parent.cell_size + margin
                    y1 = canvas_y * self.parent.cell_size + margin
                    x2 = (x + 1) * self.parent.cell_size - margin
                    y2 = (canvas_y + 1) * self.parent.cell_size - margin
                    self.parent.canvas.create_rectangle(x1, y1, x2, y2, fill='lightblue', outline='blue', tags='visited')
                
                # Draw percepts on ALL cells (not just visited ones)
                if not self.parent.env.has_gold(x, y) and not self.parent.env.has_wumpus(x, y) and not self.parent.env.has_pit(x, y):
                    self.draw_percepts_on_cell(x, canvas_y)
                
                # Draw wumpus
                if self.parent.env.has_wumpus(x, y):
                    margin = max(3, self.parent.cell_size // 20)  # Dynamic margin (3-6px depending on cell size)
                    x1 = x * self.parent.cell_size + margin
                    y1 = canvas_y * self.parent.cell_size + margin
                    x2 = (x + 1) * self.parent.cell_size - margin
                    y2 = (canvas_y + 1) * self.parent.cell_size - margin
                    border_width = max(1, self.parent.cell_size // 40)  # Dynamic border width
                    self.parent.canvas.create_rectangle(x1, y1, x2, y2, fill='red', outline='darkred', width=border_width, tags='wumpus')
                    font_size = max(8, self.parent.cell_size // 6)  # Dynamic font size
                    self.parent.canvas.create_text(x * self.parent.cell_size + self.parent.cell_size//2,
                                          canvas_y * self.parent.cell_size + self.parent.cell_size//2,
                                          text='W', fill='white', font=('Arial', font_size, 'bold'), tags='wumpus')
                
                # Draw pits
                if self.parent.env.has_pit(x, y):
                    margin = max(3, self.parent.cell_size // 20)  # Dynamic margin (scales with cell size)
                    x1 = x * self.parent.cell_size + margin
                    y1 = canvas_y * self.parent.cell_size + margin
                    x2 = (x + 1) * self.parent.cell_size - margin
                    y2 = (canvas_y + 1) * self.parent.cell_size - margin
                    border_width = max(1, self.parent.cell_size // 40)  # Dynamic border width
                    self.parent.canvas.create_rectangle(x1, y1, x2, y2, fill='black', outline='gray', width=border_width, tags='pit')
                    font_size = max(6, self.parent.cell_size // 8)  # Dynamic font size for pit text
                    self.parent.canvas.create_text(x * self.parent.cell_size + self.parent.cell_size//2,
                                          canvas_y * self.parent.cell_size + self.parent.cell_size//2,
                                          text='P', fill='white', font=('Arial', font_size, 'bold'), tags='pit')
                
                # Draw gold
                if self.parent.env.has_gold(x, y):
                    margin = max(10, self.parent.cell_size // 6)  # Dynamic margin for gold
                    x1 = x * self.parent.cell_size + margin
                    y1 = canvas_y * self.parent.cell_size + margin
                    x2 = (x + 1) * self.parent.cell_size - margin
                    y2 = (canvas_y + 1) * self.parent.cell_size - margin
                    border_width = max(1, self.parent.cell_size // 40)  # Dynamic border width
                    self.parent.canvas.create_oval(x1, y1, x2, y2, fill='gold', outline='orange', width=border_width, tags='gold')
                    font_size = max(6, self.parent.cell_size // 8)  # Dynamic font size for gold text
                    self.parent.canvas.create_text(x * self.parent.cell_size + self.parent.cell_size//2,
                                          canvas_y * self.parent.cell_size + self.parent.cell_size//2,
                                          text='Gold', fill='black', font=('Arial', font_size, 'bold'), tags='gold')
    
    def draw_percepts_on_cell(self, x, canvas_y):
        """Draw percept indicators on all cells"""
        # Convert canvas_y back to world y for percept calculation
        world_y = (self.parent.height - 1 - canvas_y)
        
        # Calculate percepts directly for this cell
        percepts = {
            'stench': False,
            'breeze': False,
            'glitter': False
        }
        
        # Check for stench (adjacent to wumpus)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            adj_x, adj_y = x + dx, world_y + dy
            if 0 <= adj_x < self.parent.width and 0 <= adj_y < self.parent.height:
                if self.parent.env.has_wumpus(adj_x, adj_y):
                    percepts['stench'] = True
                    break
        
        # Check for breeze (adjacent to pit)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            adj_x, adj_y = x + dx, world_y + dy
            if 0 <= adj_x < self.parent.width and 0 <= adj_y < self.parent.height:
                if self.parent.env.has_pit(adj_x, adj_y):
                    percepts['breeze'] = True
                    break
        
        # Check for glitter (gold in same cell)
        if self.parent.env.has_gold(x, world_y):
            percepts['glitter'] = True
        
        # Calculate center position for percept indicators (using canvas coordinates)
        cell_x = x * self.parent.cell_size
        cell_y = canvas_y * self.parent.cell_size
        center_x = cell_x + self.parent.cell_size // 2
        center_y = cell_y + self.parent.cell_size // 2
        
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
            radius = max(12, self.parent.cell_size // 12)  # Dynamic radius based on cell size
            self.parent.canvas.create_oval(center_x - radius, center_y - radius, 
                                  center_x + radius, center_y + radius, 
                                  fill=fill_color, outline=outline_color, width=2, tags='percept')
            font_size = max(7, self.parent.cell_size // 12)  # Dynamic font size for percepts
            self.parent.canvas.create_text(center_x, center_y, text=text, 
                                  fill=text_color, font=('Arial', font_size, 'bold'), tags='percept')
        
        elif len(percept_list) == 2:
            # Two percepts - arrange vertically
            for i, (text, fill_color, outline_color, text_color) in enumerate(percept_list):
                radius = max(8, self.parent.cell_size // 10)  # Slightly smaller for multiple percepts
                y_offset = (-radius*0.8) if i == 0 else (radius*0.8)  # Dynamic spacing
                self.parent.canvas.create_oval(center_x - radius, center_y + y_offset - radius, 
                                      center_x + radius, center_y + y_offset + radius, 
                                      fill=fill_color, outline=outline_color, width=2, tags='percept')
                font_size = max(4, self.parent.cell_size // 15)  # Smaller font for multiple percepts
                self.parent.canvas.create_text(center_x, center_y + y_offset, text=text, 
                                      fill=text_color, font=('Arial', font_size, 'bold'), tags='percept')
        
        elif len(percept_list) == 3:
            # Three percepts - arrange in triangle pattern
            radius = max(6, self.parent.cell_size // 12)  # Even smaller for three percepts
            spacing = radius * 1.2  # Dynamic spacing based on radius
            positions = [(-spacing, -spacing*0.6), (spacing, -spacing*0.6), (0, spacing)]  # top-left, top-right, bottom
            for i, (text, fill_color, outline_color, text_color) in enumerate(percept_list):
                x_offset, y_offset = positions[i]
                self.parent.canvas.create_oval(center_x + x_offset - radius, center_y + y_offset - radius, 
                                      center_x + x_offset + radius, center_y + y_offset + radius, 
                                      fill=fill_color, outline=outline_color, width=2, tags='percept')
                font_size = max(3, self.parent.cell_size // 18)  # Smallest font for three percepts
                self.parent.canvas.create_text(center_x + x_offset, center_y + y_offset, text=text, 
                                      fill=text_color, font=('Arial', font_size, 'bold'), tags='percept')
    
    def draw_agent(self):
        """Draw the agent on the board"""
        x, y = self.parent.agent.x, self.parent.agent.y
        # Convert to canvas coordinates (flip Y-axis so (0,0) is bottom-left)
        canvas_y = (self.parent.height - 1 - y)
        
        margin = max(8, self.parent.cell_size // 12)  # Dynamic margin for agent
        x1 = x * self.parent.cell_size + margin
        y1 = canvas_y * self.parent.cell_size + margin
        x2 = (x + 1) * self.parent.cell_size - margin
        y2 = (canvas_y + 1) * self.parent.cell_size - margin
        
        # Agent color based on status
        color = 'hotpink' if self.parent.agent.alive else 'red'
        if self.parent.agent.has_gold:
            color = 'green'
        
        border_width = max(1, self.parent.cell_size // 40)  # Dynamic border width
        self.parent.canvas.create_oval(x1, y1, x2, y2, fill=color, outline='darkblue', width=border_width, tags='agent')
        
        # Direction arrow
        center_x = x * self.parent.cell_size + self.parent.cell_size//2
        center_y = canvas_y * self.parent.cell_size + self.parent.cell_size//2
        
        arrow_length = max(8, self.parent.cell_size // 6)  # Dynamic arrow length
        arrow_width = max(2, self.parent.cell_size // 30)  # Dynamic arrow width
        if self.parent.agent.dir == 'N':
            end_x, end_y = center_x, center_y - arrow_length
        elif self.parent.agent.dir == 'E':
            end_x, end_y = center_x + arrow_length, center_y
        elif self.parent.agent.dir == 'S':
            end_x, end_y = center_x, center_y + arrow_length
        else:  # W
            end_x, end_y = center_x - arrow_length, center_y
            
        self.parent.canvas.create_line(center_x, center_y, end_x, end_y, 
                              fill='white', width=arrow_width, arrow=tk.LAST, tags='agent')
    
    def update_display(self):
        """Update the status display with current game information"""
        # Update status labels
        self.parent.position_label.config(text=f"Agent Position: ({self.parent.agent.x}, {self.parent.agent.y})")
        self.parent.direction_label.config(text=f"Agent Direction: {self.parent.agent.dir}")
        self.parent.score_label.config(text=f"Score: {self.parent.agent.score}")
        self.parent.steps_label.config(text=f"Steps: {self.parent.steps}")
        
        # Reset scream if it was triggered
        if self.parent.env.get_scream():
            self.parent.env.reset_scream()  # Reset scream after checking
    
    def add_move_to_history(self, action, position, direction, result=""):
        """Add a move to the history display"""
        move_num = len(self.parent.moves_history) + 1
        
        move_entry = {
            'number': move_num,
            'action': action,
            'position': position,
            'direction': direction,
            'result': result
        }
        
        self.parent.moves_history.append(move_entry)
        
        # Format move for display
        move_text = f"{move_num:2d}. {action:12s} -> ({position[0]},{position[1]})" 
        if result:
            move_text += f" | {result}"
        move_text += "\n"
        
        # Add to text widget
        self.parent.moves_text.insert(tk.END, move_text)
        self.parent.moves_text.see(tk.END)  # Scroll to bottom
        
        # Limit history to last 50 moves to prevent memory issues
        if len(self.parent.moves_history) > 50:
            self.parent.moves_history = self.parent.moves_history[-50:]
            # Clear and reload text widget
            self.parent.moves_text.delete(1.0, tk.END)
            for move in self.parent.moves_history:
                move_text = f"{move['number']:2d}. {move['action']:12s} -> ({move['position'][0]},{move['position'][1]}) {move['direction']}"
                if move['result']:
                    move_text += f" | {move['result']}"
                move_text += "\n"
                self.parent.moves_text.insert(tk.END, move_text)
