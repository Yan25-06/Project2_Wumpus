import tkinter as tk
from tkinter import ttk, messagebox
import io
import sys
import threading
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
        
        if self.parent.agent.steps > 100:
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
        """Reset the game to initial state with a new random map"""
        self.stop_game()
        
        # Use stored settings or defaults
        board_size = getattr(self.parent, 'board_size', 8)
        pit_probability = getattr(self.parent, 'pit_probability', 0.2)
        wumpus_count = getattr(self.parent, 'wumpus_count', 2)
        
        # Always create a new random environment when reset is pressed
        # Use current time as seed if no seed provided to ensure randomness
        import time
        reset_seed = seed if seed is not None else int(time.time() * 1000) % 10000
        
        print(f"Reset: Creating new random environment with seed {reset_seed}")
        self.parent.env = Environment(N=board_size, K=wumpus_count, 
                                    pit_prob=pit_probability, seed=reset_seed)
        
        # Create agent based on current mode
        if self.parent.agent_mode == "Random":
            self.parent.agent = RandomAgent(self.parent.env)
        else:  # Hybrid
            self.parent.agent = HybridAgent(self.parent.env)
        self.parent.game_over = False
        self.parent.moves_history = []  # Clear moves history
        self.parent.moves_text.delete(1.0, tk.END)  # Clear moves display
        self.parent.status_label.config(text="Game Reset - New random map generated")
        self.parent.start_button.config(state='normal')
        self.parent.draw_ui.draw_board()
        self.parent.draw_ui.update_display()
    
    def change_board_size(self):
        if self.parent.game_running:
            messagebox.showwarning("Cannot Change", "Stop the game before changing settings!")
            return
            
        # Show settings dialog
        settings_window = tk.Toplevel(self.parent)
        settings_window.title("Game Settings")
        settings_window.geometry("500x800")
        settings_window.resizable(False, False)
        
        settings_window.transient(self.parent)
        settings_window.grab_set()
        
        # Main container
        main_container = ttk.Frame(settings_window, padding=20)
        main_container.pack(fill='both', expand=True)
        
        ttk.Label(main_container, text="Game Configuration Settings", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Agent Mode Section
        agent_frame = ttk.LabelFrame(main_container, text="Agent Type", padding=15)
        agent_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(agent_frame, text="Select the type of agent to use:", font=('Arial', 10)).pack(anchor='w')
        
        agent_mode_var = tk.StringVar(value=getattr(self.parent, 'agent_mode', 'Hybrid'))
        
        agent_radio_frame = ttk.Frame(agent_frame)
        agent_radio_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Radiobutton(agent_radio_frame, text="Random Agent", 
                      variable=agent_mode_var, value="Random").pack(side='left', padx=(0, 20))
        ttk.Radiobutton(agent_radio_frame, text="Hybrid Agent (AI)", 
                      variable=agent_mode_var, value="Hybrid").pack(side='left')
        
        # Board Size Section
        board_frame = ttk.LabelFrame(main_container, text="Board Size", padding=15)
        board_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(board_frame, text="Select board dimensions:", font=('Arial', 10)).pack(anchor='w')
        
        board_size_var = tk.IntVar(value=getattr(self.parent, 'board_size', 8))
        board_sizes = [2, 3, 4, 5, 6, 7, 8]
        
        board_radio_frame = ttk.Frame(board_frame)
        board_radio_frame.pack(fill='x', pady=(5, 0))
        
        for i, size in enumerate(board_sizes):
            row = i // 3
            col = i % 3
            ttk.Radiobutton(board_radio_frame, text=f"{size}x{size}", 
                          variable=board_size_var, value=size).grid(row=row, column=col, 
                          sticky='w', padx=(0, 20), pady=2)

        # Environment Seed Section
        seed_frame = ttk.LabelFrame(main_container, text="Environment Seed", padding=15)
        seed_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(seed_frame, text="Random seed for environment generation (1 to 20):", 
                 font=('Arial', 10)).pack(anchor='w')
        
        seed_var = tk.IntVar(value=getattr(self.parent, 'seed', 1))
        
        seed_frame_inner = ttk.Frame(seed_frame)
        seed_frame_inner.pack(fill='x', pady=(5, 0))
        
        # Input field for seed
        ttk.Label(seed_frame_inner, text="Seed:").pack(side='left')
        seed_entry = ttk.Entry(seed_frame_inner, textvariable=seed_var, width=10)
        seed_entry.pack(side='left', padx=(5, 10))
        
        # Pit Probability Section
        pit_frame = ttk.LabelFrame(main_container, text="Pit Probability", padding=15)
        pit_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(pit_frame, text="Probability of pits appearing in each cell (0.05 to 0.5):", 
                 font=('Arial', 10)).pack(anchor='w')
        
        pit_prob_var = tk.DoubleVar(value=getattr(self.parent, 'pit_probability', 0.1))
        
        pit_frame_inner = ttk.Frame(pit_frame)
        pit_frame_inner.pack(fill='x', pady=(5, 0))
        
        # Input for pit probability
        ttk.Label(pit_frame_inner, text="Pit Probability:").pack(side='left')
        pit_entry = ttk.Entry(pit_frame_inner, textvariable=pit_prob_var, width=10)
        pit_entry.pack(side='left', padx=(5, 10))
        
        pit_percentage_label = ttk.Label(pit_frame_inner, text="10.0%")
        pit_percentage_label.pack(side='left')
        
        def update_pit_percentage(*args):
            try:
                value = pit_prob_var.get()
                pit_percentage_label.config(text=f"{value:.1%}")
            except:
                pit_percentage_label.config(text="Invalid")
        
        pit_prob_var.trace('w', update_pit_percentage)
        update_pit_percentage()  
        
        # Number of Wumpus Section
        wumpus_frame = ttk.LabelFrame(main_container, text="Number of Wumpus", padding=15)
        wumpus_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(wumpus_frame, text="Number of Wumpus creatures on the board (1 to 10):", 
                 font=('Arial', 10)).pack(anchor='w')
        
        wumpus_var = tk.IntVar(value=getattr(self.parent, 'wumpus_count', 2))
        
        wumpus_frame_inner = ttk.Frame(wumpus_frame)
        wumpus_frame_inner.pack(fill='x', pady=(5, 0))
        
        # Input for number of wumpus
        ttk.Label(wumpus_frame_inner, text="Wumpus Count:").pack(side='left')
        wumpus_entry = ttk.Entry(wumpus_frame_inner, textvariable=wumpus_var, width=10)
        wumpus_entry.pack(side='left', padx=(5, 10))
        
        
        
        def apply_settings():
            try:
                new_agent_mode = agent_mode_var.get()
                new_board_size = board_size_var.get()
                new_pit_prob = pit_prob_var.get()
                new_wumpus_count = wumpus_var.get()
                new_seed = seed_var.get()
                
                # Validate pit probability
                if not (0.05 <= new_pit_prob <= 0.5):
                    messagebox.showerror("Invalid Settings", 
                                       f"Pit probability must be between 0.05 (5%) and 0.5 (50%)!\n"
                                       f"Current value: {new_pit_prob:.3f}")
                    return
                
                # Validate wumpus count
                if not (1 <= new_wumpus_count <= 10):
                    messagebox.showerror("Invalid Settings", 
                                       f"Number of Wumpus must be between 1 and 10!\n"
                                       f"Current value: {new_wumpus_count}")
                    return
                
                # Validate seed
                if not (1 <= new_seed <= 20):
                    messagebox.showerror("Invalid Settings", 
                                       f"Seed must be between 1 and 20!\n"
                                       f"Current value: {new_seed}")
                    return
                
                # Validate wumpus count vs board size
                max_wumpus = int(new_board_size * new_board_size * 0.4)  # Max 40% of cells
                if new_wumpus_count > max_wumpus:
                    messagebox.showerror("Invalid Settings", 
                                       f"Too many Wumpus for a {new_board_size}x{new_board_size} board!\n"
                                       f"Maximum recommended: {max_wumpus}\n"
                                       f"Current value: {new_wumpus_count}")
                    return
                
            except ValueError:
                messagebox.showerror("Invalid Input", 
                                   "Please enter valid numbers for pit probability, wumpus count, and seed.")
                return
            
            # Check if only agent mode changed (keep same map)
            agent_mode_changed = new_agent_mode != getattr(self.parent, 'agent_mode', 'Hybrid')
            settings_changed = (new_board_size != getattr(self.parent, 'board_size', 8) or
                              new_pit_prob != getattr(self.parent, 'pit_probability', 0.2) or
                              new_wumpus_count != getattr(self.parent, 'wumpus_count', 2) or
                              new_seed != getattr(self.parent, 'seed', 1))
            
            # Store new settings
            self.parent.agent_mode = new_agent_mode
            self.parent.board_size = new_board_size
            self.parent.pit_probability = new_pit_prob
            self.parent.wumpus_count = new_wumpus_count
            self.parent.seed = new_seed
            self.parent.width = new_board_size
            self.parent.height = new_board_size
            
            # Update UI button texts
            self.parent.size_button.config(text="SETTINGS")
            self.parent.agent_button.config(text=f"AGENT: {new_agent_mode}")
            
            # Recalculate cell size based on new board size
            screen_width = self.parent.winfo_screenwidth()
            screen_height = self.parent.winfo_screenheight()
            available_width = screen_width - 600  
            available_height = screen_height - 250  
            
            # Calculate optimal cell size for new board size
            max_cell_width = available_width // self.parent.width
            max_cell_height = available_height // self.parent.height
            self.parent.cell_size = min(max_cell_width, max_cell_height, 120)  
            
            print(f"Settings update - Agent: {new_agent_mode}, Board: {new_board_size}x{new_board_size}, "
                  f"Pit Prob: {new_pit_prob:.1%}, Wumpus: {new_wumpus_count}, Seed: {new_seed}, "
                  f"Cell size: {self.parent.cell_size}px")
            
            # Handle environment recreation based on what changed
            if settings_changed:
                # Environment settings changed - create new random environment
                print("Creating new random environment due to setting changes")
                self.parent.env = Environment(N=new_board_size, K=new_wumpus_count, 
                                            pit_prob=new_pit_prob, seed=new_seed)
                change_message = "Environment settings changed - new random map generated"
            elif agent_mode_changed:
                # Agent mode changed - create fresh environment with same seed to restore original state
                print("Agent mode changed - creating fresh environment with same seed to restore original state")
                self.parent.env = Environment(N=new_board_size, K=new_wumpus_count, 
                                            pit_prob=new_pit_prob, seed=new_seed)
                change_message = "Agent type changed - fresh environment created with same layout and restored wumpus"
            else:
                change_message = "No changes detected"
            
            # Create agent based on new mode
            if new_agent_mode == "Random":
                self.parent.agent = RandomAgent(self.parent.env)
            else:  
                self.parent.agent = HybridAgent(self.parent.env)
            
            if hasattr(self.parent.agent, 'visited'):
                self.parent.agent.visited = {(0, 0)}  
            
            if settings_changed:
                self.parent.canvas.config(width=self.parent.width * self.parent.cell_size, 
                                 height=self.parent.height * self.parent.cell_size)
            
            # Reset game state
            self.parent.game_over = False
            self.parent.moves_history = []
            self.parent.moves_text.delete(1.0, tk.END)
            
            self.parent.draw_ui.draw_board()
            self.parent.draw_ui.update_display()
            
            settings_window.destroy()
            
            if agent_mode_changed and not settings_changed:
                messagebox.showinfo("Agent Changed", 
                                  f"Agent type changed to: {new_agent_mode}\n"
                                  f"Fresh environment created with same layout.\n"
                                  f"All wumpus and gold restored to original positions.")
            else:
                messagebox.showinfo("Settings Applied", 
                                  f"Game settings updated:\n"
                                  f"• Agent Type: {new_agent_mode}\n"
                                  f"• Board Size: {new_board_size}x{new_board_size}\n"
                                  f"• Pit Probability: {new_pit_prob:.1%}\n"
                                  f"• Wumpus Count: {new_wumpus_count}\n"
                                  f"• Seed: {new_seed}\n"
                                  f"• Cell Size: {self.parent.cell_size}px\n\n"
                                  f"{change_message}")
        
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=(20, 0))
        
        # Style the buttons
        apply_btn = ttk.Button(button_frame, text="Apply Settings", command=apply_settings)
        apply_btn.pack(side='left', padx=(0, 10), ipadx=20, ipady=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=settings_window.destroy)
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
            def update_ui(text):
                """Thread-safe UI update"""
                compare_window.after(0, lambda: results_text.insert(tk.END, text))
                compare_window.after(0, lambda: results_text.update())
            
            def finish_comparison():
                """Finish the comparison and show close button"""
                compare_window.after(0, lambda: progress.stop())
                compare_window.after(0, lambda: progress.pack_forget())
                
                # Close button
                def add_close_button():
                    close_frame = ttk.Frame(main_container)
                    close_frame.pack(pady=(20, 0))
                    ttk.Button(close_frame, text="Close", 
                              command=compare_window.destroy).pack()
                
                compare_window.after(0, add_close_button)
            
            try:
                # Get the original environment configuration
                board_size = getattr(self.parent, 'board_size', 8)
                pit_probability = getattr(self.parent, 'pit_probability', 0.2)
                wumpus_count = getattr(self.parent, 'wumpus_count', 2)
                original_seed = self.parent.seed
                
                update_ui("=== AGENT COMPARISON RESULTS ===\n\n")
                update_ui(f"Board Size: {board_size}x{board_size}\n")
                update_ui(f"Pit Probability: {pit_probability:.1%}\n")
                update_ui(f"Wumpus Count: {wumpus_count}\n")
                update_ui(f"Seed: {original_seed}\n\n")
                
                # Test both agents on completely fresh environments
                agent_results = {}
                
                for agent_name in ["Random", "Hybrid"]:
                    update_ui(f"--- Testing {agent_name} Agent ---\n")
                    
                    # Create a completely fresh environment with the same seed and configuration
                    # This ensures both agents get exactly the same original map
                    test_env = Environment(N=board_size, K=wumpus_count, 
                                         pit_prob=pit_probability, seed=original_seed)
                    
                    # Set agent to starting position
                    test_env.set_agent_pos_and_dir(0, 0, 'E')
                    
                    # Create agent
                    if agent_name == "Random":
                        test_agent = RandomAgent(test_env)
                    else:
                        test_agent = HybridAgent(test_env)
                    
                    # Run agent with step limit
                    max_steps = 500
                    game_outcome = "Unknown"
                    
                    while test_agent.steps < max_steps and test_agent.alive:
                        continue_game = test_agent.step()
                        
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

                    if test_agent.steps >= max_steps:
                        game_outcome = "Timeout (500+ steps)"
                    
                    # Store results
                    agent_results[agent_name] = {
                        'steps': test_agent.steps,
                        'score': test_agent.score,
                        'outcome': game_outcome,
                        'has_gold': test_agent.has_gold,
                        'alive': test_agent.alive,
                        'can_shoot': test_agent.can_shoot
                    }
                    
                    # Display results
                    update_ui(f"  Steps: {test_agent.steps}\n")
                    update_ui(f"  Final Score: {test_agent.score}\n")
                    update_ui(f"  Outcome: {game_outcome}\n")
                    update_ui(f"  Has Gold: {test_agent.has_gold}\n")
                    update_ui(f"  Can shoot: {test_agent.can_shoot}\n\n")
                
                # Summary comparison
                update_ui("=== COMPARISON SUMMARY ===\n\n")
                
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
                
                update_ui(f"Winner: {winner} Agent\n\n")
                
                # Detailed comparison
                update_ui("Score Comparison:\n")
                update_ui(f"  Random Agent: {random_result['score']}\n")
                update_ui(f"  Hybrid Agent: {hybrid_result['score']}\n\n")
                
                update_ui("Steps Comparison:\n")
                update_ui(f"  Random Agent: {random_result['steps']}\n")
                update_ui(f"  Hybrid Agent: {hybrid_result['steps']}\n\n")
                
                update_ui("Outcome Comparison:\n")
                update_ui(f"  Random Agent: {random_result['outcome']}\n")
                update_ui(f"  Hybrid Agent: {hybrid_result['outcome']}\n\n")
                
                # Efficiency analysis
                if winner != "Tie":
                    winning_agent = agent_results[winner]
                    losing_agent = agent_results["Random" if winner == "Hybrid" else "Hybrid"]
                    
                    score_diff = winning_agent['score'] - losing_agent['score']
                    step_diff = winning_agent['steps'] - losing_agent['steps']
                    
                    update_ui(f"Performance Analysis:\n")
                    update_ui(f"  {winner} agent scored {score_diff} points better\n")
                    
                    if step_diff < 0:
                        update_ui(f"  {winner} agent was {abs(step_diff)} steps more efficient\n")
                    elif step_diff > 0:
                        update_ui(f"  {winner} agent took {step_diff} more steps\n")
                    else:
                        update_ui(f"  Both agents took the same number of steps\n")
                
                finish_comparison()
                
            except Exception as e:
                def show_error():
                    progress.stop()
                    results_text.insert(tk.END, f"Error during comparison: {str(e)}\n")
                    messagebox.showerror("Comparison Error", f"An error occurred: {str(e)}")
                
                compare_window.after(0, show_error)
        
        # Run comparison in a separate thread to avoid blocking UI  
        comparison_thread = threading.Thread(target=run_comparison, daemon=True)
        comparison_thread.start()
    
    def run_agent(self):
        """Run the agent continuously"""
        if not self.parent.game_running or self.parent.game_over:
            return
            
        self.single_step()
        
        # Schedule next move if game is still running
        if self.parent.game_running and not self.parent.game_over and self.parent.agent.alive:
            self.parent.after(600, self.run_agent)  # Move every second
        else:
            self.stop_game()
