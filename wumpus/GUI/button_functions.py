import tkinter as tk
from tkinter import ttk, messagebox
import io
import sys
from ..core.environment import Environment
from ..agents.random_agent import RandomAgent
from ..agents.hybrid_agent import HybridAgent


class ButtonFunctions:
    """Handles all button functionality and game logic for the Wumpus World game"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def single_step(self):
        """Execute a single step of the agent's action"""
        if self.parent.game_over or not self.parent.agent.alive:
            return
        
        # Record state before action
        prev_pos = (self.parent.agent.x, self.parent.agent.y)
        prev_dir = self.parent.agent.dir
        prev_score = self.parent.agent.score
        prev_has_gold = self.parent.agent.has_gold
        prev_can_shoot = self.parent.agent.can_shoot
        
        # Get current percepts before action
        current_percepts = self.parent.env.get_percepts(self.parent.agent.x, self.parent.agent.y)
        
        # Capture stdout to get agent's print messages
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        try:
            # Execute agent step
            continue_game = self.parent.agent.step()
            self.parent.steps += 1
        finally:
            # Restore stdout
            sys.stdout = old_stdout
        
        # Get the captured output (agent's print messages)
        agent_messages = captured_output.getvalue().strip()
        
        # Determine what action was taken by comparing states
        new_pos = (self.parent.agent.x, self.parent.agent.y)
        new_dir = self.parent.agent.dir
        new_score = self.parent.agent.score
        new_has_gold = self.parent.agent.has_gold
        
        # Use agent's printed message as the action, or fall back to detecting action
        if agent_messages:
            action_taken = agent_messages
        else:
            # Fallback action detection
            if new_pos != prev_pos:
                action_taken = f"Agent moved to ({new_pos[0]}, {new_pos[1]}) facing {new_dir}"
                if not self.parent.agent.alive:
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
                action_taken = "Agent shot and " + ("killed the Wumpus!" if self.parent.env.get_scream() else "missed.")
            elif not continue_game and (self.parent.agent.x, self.parent.agent.y) == (0, 0):
                action_taken = f"Agent climbed out {'with' if self.parent.agent.has_gold else 'without'} the gold!"
            else:
                action_taken = "Unknown action"
        
        result = ""
        if not self.parent.agent.alive:
            result = "DIED!"
        elif self.parent.agent.has_gold and not prev_has_gold:
            result = "GOT GOLD!"
        elif self.parent.env.get_scream():
            result = "HIT WUMPUS!"
        
        # Add move to history with agent's exact message
        self.parent.draw_ui.add_move_to_history(action_taken, new_pos, new_dir, result)
        
        if not continue_game or not self.parent.agent.alive:
            self.parent.game_over = True
            if not self.parent.agent.alive:
                self.parent.status_label.config(text="Game Over! Agent died!")
                messagebox.showwarning("Game Over", "Agent died!")
            elif self.parent.agent.has_gold and (self.parent.agent.x, self.parent.agent.y) == (0, 0):
                self.parent.status_label.config(text="Success! Agent climbed out with gold!")
                messagebox.showinfo("Success", f"Agent won! Final Score: {self.parent.agent.score}")
            else:
                self.parent.status_label.config(text="Game ended")
        
        if self.parent.steps > 100:
            self.parent.game_over = True
            self.parent.status_label.config(text="Game Over! Too many steps!")
            messagebox.showwarning("Game Over", "Agent took too many steps!")
        
        self.parent.draw_ui.draw_board()
        self.parent.draw_ui.update_display()
    
    def start_game(self):
        """Start the game"""
        if not self.parent.game_over:
            self.parent.game_running = True
            self.parent.start_button.config(state='disabled')
            self.parent.stop_button.config(state='normal')
            self.parent.status_label.config(text="Agent is exploring...")
            self.run_agent()
    
    def stop_game(self):
        """Stop the game"""
        self.parent.game_running = False
        self.parent.start_button.config(state='normal')
        self.parent.stop_button.config(state='disabled')
        self.parent.status_label.config(text="Agent stopped")

    def reset_game(self, seed=None):
        """Reset the game to initial state"""
        self.stop_game()
        self.parent.env = Environment(N=self.parent.board_size, seed=seed)
        # Create agent based on current mode
        if self.parent.agent_mode == "Random":
            self.parent.agent = RandomAgent(self.parent.env)
        else:  # Hybrid
            self.parent.agent = HybridAgent(self.parent.env)
        self.parent.game_over = False
        self.parent.steps = 0
        self.parent.moves_history = []  # Clear moves history
        self.parent.moves_text.delete(1.0, tk.END)  # Clear moves display
        self.parent.status_label.config(text="Game Reset - Click Start Agent to begin")
        self.parent.start_button.config(state='normal')
        self.parent.draw_ui.draw_board()
        self.parent.draw_ui.update_display()
    
    def toggle_agent_mode(self):
        """Toggle between Random and Hybrid agent modes"""
        if self.parent.game_running:
            messagebox.showwarning("Cannot Change", "Stop the game before changing agent mode!")
            return
            
        self.parent.agent_mode = "Hybrid" if self.parent.agent_mode == "Random" else "Random"
        self.parent.agent_button.config(text=f"AGENT: {self.parent.agent_mode}")
        
        # Recreate agent with new mode
        if self.parent.agent_mode == "Random":
            self.parent.agent = RandomAgent(self.parent.env)
        else:  # Hybrid
            self.parent.agent = HybridAgent(self.parent.env)
        
        self.parent.draw_ui.update_display()
        messagebox.showinfo("Agent Changed", f"Agent mode changed to: {self.parent.agent_mode}")
    
    def change_board_size(self):
        """Change the board size"""
        if self.parent.game_running:
            messagebox.showwarning("Cannot Change", "Stop the game before changing board size!")
            return
            
        # Show size selection dialog
        sizes = [4, 6, 8, 10, 12, 16]
        size_window = tk.Toplevel(self.parent)
        size_window.title("Select Board Size")
        size_window.geometry("400x350")
        size_window.resizable(False, False)
        
        # Center the dialog
        size_window.transient(self.parent)
        size_window.grab_set()
        
        # Main container
        main_container = ttk.Frame(size_window, padding=15)
        main_container.pack(fill='both', expand=True)
        
        ttk.Label(main_container, text="Choose Board Size:", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        selected_size = tk.IntVar(value=self.parent.board_size)
        
        # Radio buttons frame
        radio_frame = ttk.Frame(main_container)
        radio_frame.pack(pady=10)
        
        for size in sizes:
            ttk.Radiobutton(radio_frame, text=f"{size}x{size} Grid", 
                          variable=selected_size, value=size,
                          style='TRadiobutton').pack(pady=5, anchor='w')
        
        def apply_size():
            new_size = selected_size.get()
            if new_size != self.parent.board_size:
                self.parent.board_size = new_size
                self.parent.width = new_size
                self.parent.height = new_size
                self.parent.size_button.config(text=f"SIZE: {self.parent.board_size}x{self.parent.board_size}")
                
                # Recalculate cell size based on new board size
                screen_width = self.parent.winfo_screenwidth()
                screen_height = self.parent.winfo_screenheight()
                available_width = screen_width - 600  # Reserve space for right panel
                available_height = screen_height - 250  # Leave space for title and margins
                
                # Calculate optimal cell size for new board size
                max_cell_width = available_width // self.parent.width
                max_cell_height = available_height // self.parent.height
                self.parent.cell_size = min(max_cell_width, max_cell_height, 120)  # Cap at 120px for very small boards
                
                print(f"New board size: {new_size}x{new_size}, Cell size: {self.parent.cell_size}px")
                
                # Recreate environment and agent with new size
                self.parent.env = Environment(N=new_size)
                if self.parent.agent_mode == "Random":
                    self.parent.agent = RandomAgent(self.parent.env)
                else:  # Hybrid
                    self.parent.agent = HybridAgent(self.parent.env)
                
                # Update canvas size with new cell size
                self.parent.canvas.config(width=self.parent.width * self.parent.cell_size, 
                                 height=self.parent.height * self.parent.cell_size)
                
                # Reset game state
                self.parent.game_over = False
                self.parent.steps = 0
                self.parent.moves_history = []
                self.parent.moves_text.delete(1.0, tk.END)
                
                self.parent.draw_ui.draw_board()
                self.parent.draw_ui.update_display()
                
                messagebox.showinfo("Board Size Changed", f"Board size changed to: {new_size}x{new_size}\nCell size: {self.parent.cell_size}px")
            
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
        if self.parent.game_running:
            messagebox.showwarning("Cannot Compare", "Stop the current game before comparing agents!")
            return
        
        # Store current environment state to restore later
        original_env = self.parent.env
        
        # Create comparison window
        compare_window = tk.Toplevel(self.parent)
        compare_window.title("Agent Comparison Results")
        compare_window.geometry("600x500")
        compare_window.resizable(True, True)
        compare_window.transient(self.parent)
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
                saved_wumpus_pos = []
                saved_pit_positions = []
                saved_gold_pos = None
                
                # Find current positions
                for y in range(self.parent.height):
                    for x in range(self.parent.width):
                        if self.parent.env.has_wumpus(x, y):
                            saved_wumpus_pos.append((x, y))
                        if self.parent.env.has_pit(x, y):
                            saved_pit_positions.append((x, y))
                        if self.parent.env.has_gold(x, y):
                            saved_gold_pos = (x, y)
                
                results_text.insert(tk.END, "=== AGENT COMPARISON RESULTS ===\n\n")
                results_text.insert(tk.END, f"Board Size: {self.parent.board_size}x{self.parent.board_size}\n")
                results_text.insert(tk.END, f"Wumpus Position: {saved_wumpus_pos}\n")
                results_text.insert(tk.END, f"Pit Positions: {saved_pit_positions}\n") 
                results_text.insert(tk.END, f"Gold Position: {saved_gold_pos}\n\n")
                
                # Test both agents
                agent_results = {}
                
                for agent_name in ["Random", "Hybrid"]:
                    results_text.insert(tk.END, f"--- Testing {agent_name} Agent ---\n")
                    results_text.update()
                    
                    # Create new environment with same configuration
                    test_env = Environment(N=self.parent.board_size)
                    
                    # Clear the randomly generated elements first
                    for env_y in range(self.parent.board_size):
                        for env_x in range(self.parent.board_size):
                            if test_env.has_wumpus(env_x, env_y):
                                test_env._Environment__grid[env_y][env_x].has_wumpus = False
                            if test_env.has_pit(env_x, env_y):
                                test_env._Environment__grid[env_y][env_x].has_pit = False
                            if test_env.has_gold(env_x, env_y):
                                test_env._Environment__grid[env_y][env_x].has_gold = False
                    
                    # Reset wumpus count and scream
                    test_env._Environment__wumpus = len(saved_wumpus_pos)
                    test_env._Environment__scream = False
                    
                    # Restore the exact same map configuration
                    for wx, wy in saved_wumpus_pos:
                        test_env._Environment__grid[wy][wx].has_wumpus = True
                    
                    for pit_x, pit_y in saved_pit_positions:
                        test_env._Environment__grid[pit_y][pit_x].has_pit = True
                    
                    if saved_gold_pos:
                        gx, gy = saved_gold_pos
                        test_env._Environment__grid[gy][gx].has_gold = True
                    
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
                        'alive': test_agent.alive,
                        'can_shoot': test_agent.can_shoot
                    }
                    
                    # Display results
                    results_text.insert(tk.END, f"  Steps: {steps}\n")
                    results_text.insert(tk.END, f"  Final Score: {test_agent.score}\n")
                    results_text.insert(tk.END, f"  Outcome: {game_outcome}\n")
                    results_text.insert(tk.END, f"  Has Gold: {test_agent.has_gold}\n")
                    results_text.insert(tk.END, f"  Can shoot: {test_agent.can_shoot}\n\n")
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
        """Run the agent continuously"""
        if not self.parent.game_running or self.parent.game_over:
            return
            
        self.single_step()
        
        # Schedule next move if game is still running
        if self.parent.game_running and not self.parent.game_over and self.parent.agent.alive:
            self.parent.after(500, self.run_agent)  # Move every second
        else:
            self.stop_game()
