from ..agents.agent import Agent
from .inference_engine import KnowledgeBase

# Implement A* or other planning algorithms here
class PlanningModule: 

    def __init__(self, kb: KnowledgeBase): 
        self.kb = kb 

    

    # Main method to run per step
    def step(self):
        # 1. Get percepts (breeze, stench, scream, etc.)
        percepts = self.get_percepts()  
        
        # 2. Update KB with new facts (no probabilities)
        self.kb.update_kb(percepts)  
        
        # 3. Decide action (no model checking)
        action = self.decide_action()  
        
        # 4. Execute
        self.execute(action)

    def execute(self, action):
        pass 

    # def update_kb(self, percepts):
    #     x, y = self.position
    #     # Add immediate facts
    #     self.kb.append(f"visited({x},{y})")
    #     self.kb.append(f"not pit({x},{y})")  # Current cell is safe
        
    #     # Handle percepts
    #     if "breeze" in percepts:
    #         self.kb.append(f"breeze({x},{y})")
    #         # Rule: breeze(x,y) ⇒ pit in adjacent cells
    #         adj_pits = [f"pit({x+dx},{y+dy})" for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]]
    #         self.kb.append(f"breeze({x},{y}) ⇒ {' ∨ '.join(adj_pits)}")
        
    #     # Similar for stench/Wumpus

    def decide_action(self): 
        # 0. If current cell has gold, pick it up, return to exit
        # 1. Check adjacent cells for safety, use is_safe() 

        # 2. If exists a safe cell, pick one to move to 
        # 3. If all cell are unsafe, decide to shoot or retreat or randomly moveforward 

 
        pass 
        # Below is example, adapt to current project
        # x, y = self.position
        
        # # A. Check adjacent cells 
        # safe_adjacent = []
        # for (dx, dy) in [(1,0), (-1,0), (0,1), (0,-1)]:
        #     nx, ny = x + dx, y + dy
        #     if self.is_safe(nx, ny):  # Uses KB to check if "not pit(nx,ny)" is entailed
        #         safe_adjacent.append((nx, ny))
        
        # # B. Prioritize:
        # if self.has_gold: 
        #     return self.find_path_to_exit()
        # elif safe_adjacent:
        #     return self.move_to(safe_adjacent[0])  # Go to nearest safe cell
        # else:
        #     # shoot or retreat or move forward randomly
        #     return self.shoot_or_retreat()  # Last resort



    def is_safe(self, x, y):
        """Uses forward chaining to check safety"""
        # Your existing forward chaining logic here
        # Returns True if both:
        # 1. "not Pit({x},{y})" is derivable
        # 2. "not Wumpus({x},{y})" is derivable 


