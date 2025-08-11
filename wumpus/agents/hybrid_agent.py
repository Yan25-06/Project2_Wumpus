from ..agents.agent import Agent
from ..ai.inference_engine import InferenceEngine, KnowledgeBase
from ..core.environment import Environment,Cell
from ..ai.planning_module import PlanningModule
from heapdict import heapdict
from ..config.settings import DIRECTIONS, DIRECTION_VECTORS

class HybridAgent(Agent):

    def init_kb(self,kb: KnowledgeBase):
        # init kb 
        self.kb = kb
        try: 
            # read rules from rules.txt    
            with open("rules.txt", "r") as f:
                rules = f.readlines()
                for rule in rules:
                    self.kb.add_rule(rule.strip())
            with open("facts.txt", "r") as f:
                facts = f.readlines()
                for fact in facts:
                    self.kb.add_fact(fact.strip())
        except Exception as e:
            print(f"Error initializing knowledge base: {e}")
        pass 


    def __init__(self, env: Environment, kb: KnowledgeBase = None, ie: InferenceEngine = None, pm: PlanningModule = None, debug = False):
        super().__init__(env)
        if kb is None:
            kb = KnowledgeBase()
        if ie is None:
            ie = InferenceEngine(kb)
        if pm is None:
            pm = PlanningModule()
        
        self.init_kb(kb)

        self.debug = debug
        
        self.ie = ie
        self.pm = pm
        
        self.can_hunt = False
        self.to_climbout = False
        self.aimed_wumpus = (-1, -1)

        self.visited = {(0, 0)}  # Start with the initial position as visited
        self.x = 0
        self.y = 0
        self.route = []

        self.wumpus_at = []
        self.wumpus_prob: dict[tuple, float] = {}
        self.pit_prob: dict[tuple, float] = {}
        self.cell_prob: dict[tuple, float] = {} # 0: safe 1: die
        self.uncertain_cell = heapdict()

    def update_kb_and_cell_prob(self,percepts):
        n = self.env.get_size()
        adj = [
            (nx, ny)
            for nx, ny in [
                (self.x + 1, self.y),
                (self.x - 1, self.y),
                (self.x, self.y + 1),
                (self.x, self.y - 1)
            ]
            if 0 <= nx < n and 0 <= ny < n
        ]
        self.kb.update_kb(f"!Pit({self.x}, {self.y})")
        self.kb.update_kb(f"!Wumpus({self.x}, {self.y})")
        if not percepts["stench"]:
            self.kb.update_kb(f"!Stench({self.x}, {self.y})")
            for cell in adj:
                self.kb.update_kb(f"!Wumpus({cell[0]}, {cell[1]})")
        if not percepts["breeze"]:
            self.kb.update_kb(f"!Breeze({self.x}, {self.y})")
            for cell in adj:
                self.kb.update_kb(f"!Pit({cell[0]}, {cell[1]})")

        if percepts["stench"]:
            # Update KB with Stench rule: Stench(x, y) => Wumpus(adj_1) | Wumpus(adj_2) | ...
            self.kb.add_fact(f"Stench({self.x}, {self.y})")
            wumpus_conditions = ' | '.join([f"Wumpus({cell[0]}, {cell[1]})" for cell in adj])
            self.kb.add_rule(f"Stench({self.x}, {self.y}) => {wumpus_conditions}")
            wumpus_probs = {} 

            # self.kb.represent_kb()

            # Update wumpus probabilities
            for cell in adj:
                if cell in self.pm.space: 
                    continue
                if (cell not in self.cell_prob or 0 < self.cell_prob[cell] < 1):
                    self.wumpus_prob[cell] = self.ie.model_check_probability(f"Wumpus({cell[0]}, {cell[1]})")
                    wumpus_probs[cell] = self.wumpus_prob[cell]
                    if self.wumpus_prob[cell] == 1:
                        self.can_hunt = True
                        if cell not in self.wumpus_at:
                            self.wumpus_at.append(cell)
            if self.debug:
                print(f"[DEBUG] Stench detected at ({self.x}, {self.y}), updating Wumpus prob for cells: {[(cell, prob) for cell, prob in wumpus_probs.items()]}")

        if percepts["breeze"]:
            # Update KB with Breeze rule: Breeze(x, y) => Pit(adj_1) | Pit(adj_2) | ... 
            self.kb.add_fact(f"Breeze({self.x}, {self.y})")
            pit_conditions = ' | '.join([f"Pit({cell[0]}, {cell[1]})" for cell in adj])
            self.kb.add_rule(f"Breeze({self.x}, {self.y}) => {pit_conditions}")

            # Update pit probabilities
            pit_probs = {}
            for cell in adj:
                if cell in self.pm.space: 
                    continue
                if (cell not in self.cell_prob or 0 < self.cell_prob[cell] < 1):
                    self.pit_prob[cell] = self.ie.model_check_probability(f"Pit({cell[0]}, {cell[1]})")
                    pit_probs[cell] = self.pit_prob[cell]
            if self.debug:
                print(f"[DEBUG] Breeze detected at ({self.x}, {self.y}), updating Pit prob for cells: {[(cell, prob) for cell, prob in pit_probs.items()]}")



        for cell in adj:
            if cell in self.pm.space:
                continue
            if (cell in self.wumpus_prob and cell in self.pit_prob):
                self.cell_prob[cell] = 1 - (1 - self.wumpus_prob[cell]) * (1 - self.pit_prob[cell])
            elif (cell in self.wumpus_prob and self.wumpus_prob[cell] is not None):
                self.cell_prob[cell] = self.wumpus_prob[cell]
            elif (cell in self.pit_prob and self.pit_prob[cell] is not None):
                self.cell_prob[cell] = self.pit_prob[cell]
            if (cell in self.cell_prob and self.cell_prob[cell] == 0):
                self.pm.add_safe_cell(cell)
            if (cell in self.cell_prob and 0 < self.cell_prob[cell] < 1):
                self.uncertain_cell[cell] = self.cell_prob[cell]

    def add_adj_as_safe_cell(self):
        n = self.env.get_size()
        adj = [
            (self.x + 1, self.y),
            (self.x - 1, self.y),
            (self.x, self.y + 1),
            (self.x, self.y - 1)
        ]
        for cell in adj:
            cx, cy = cell
            if 0 <= cx < n and 0 <= cy < n:
                if (cell not in self.cell_prob or 0 < self.cell_prob[cell] < 1):
                    self.cell_prob[cell] = 0
                    if (0 < self.cell_prob[cell] < 1):
                        del self.uncertain_cell[cell]
                    self.pm.add_safe_cell(cell)


    def get_nearest_notvisited_safe_cell_route(self):
        current_pos = (self.x, self.y)
        candidates = [cell for cell in self.pm.space if cell not in self.visited]
        if not candidates:
            return None, None

        goal, path = self.pm.get_nearest_goal_route(current_pos, candidates, self.dir)
        if (goal != (-1, -1)):
            return goal, path
        return None, None
    
    def get_aimed_wumpus(self, is_at):
        x, y = is_at
        for wx, wy in self.wumpus_at:
            if x == wx and y != wy:
                return (wx, wy)
            if y == wy and x != wx:
                return (wx, wy)
        return None

    def find_shoot_path(self):
        current_pos = (self.x, self.y)
        shoot_candidates = []
        n = self.env.get_size()
        for wumpus in self.wumpus_at:
            wx, wy = wumpus
            for x in range(n):  
                if (x, wy) in self.pm.space and (x, wy) != wumpus:
                    shoot_candidates.append((x,wy))

            for y in range(n):
                if (wx, y) in self.pm.space and (wx, y) != wumpus:
                    shoot_candidates.append((wx,y))
        goal, path = self.pm.get_nearest_goal_route(current_pos, shoot_candidates, self.dir)
        if (goal != (-1, -1)):
            self.aimed_wumpus = self.get_aimed_wumpus(goal)
            print(goal)
            print(f"Hunt path: {path}")
            return path
        return None

    def turn_to_shoot_dir(self):
        wx, wy = self.aimed_wumpus
        ax, ay = self.x, self.y

        if ax == wx:
            if wy > ay:
                target_dir = 'N'
            else:
                target_dir = 'S'
        elif ay == wy:
            if wx > ax:
                target_dir = 'E'
            else:
                target_dir = 'W'
        else:
            return False
        
        current_idx = DIRECTIONS.index(self.dir)
        target_idx = DIRECTIONS.index(target_dir)
        diff = (target_idx - current_idx) % 4

        if diff == 1:
            self.turn_right()
        elif diff == 2:
            self.turn_right()
            self.turn_right()
        elif diff == 3:
            self.turn_left()
        return True


    def step(self):
        if not self.alive:
            if self.debug:
                print("[DEBUG] Agent is not alive. Returning False.")
            return False
        if (self.x == 0 and self.y == 0 and self.to_climbout == True):
            return False
        cur_pos = (self.x,self.y)
        self.cell_prob[cur_pos] = 0
        if (cur_pos in self.uncertain_cell):
            del self.uncertain_cell[cur_pos]

        self.pm.add_safe_cell(cur_pos)
        percepts = self.env.get_percepts(self.x, self.y)
        if percepts["glitter"]:
            if self.debug:
                print("[DEBUG] Glitter detected. Grabbing gold and planning route to exit.")
            self.grab_gold()
            self.route,_ = self.pm.find_route((self.x, self.y),(0,0),self.dir)
        if self.has_gold and self.x == 0 and self.y == 0: # has gold and at exit
            if self.debug:
                print("[DEBUG] Agent has gold and is at exit. Returning False.")
            return False
        if not percepts["stench"] and not percepts["breeze"]:
            if self.debug:
                print("[DEBUG] No stench or breeze. Adding adjacent cells as safe.")
            self.add_adj_as_safe_cell()

        # update kb 
        if self.debug:
            print(f"[DEBUG] Percepts: {percepts}. Updating KB and cell probabilities.")
            # self.kb.represent_kb()
        
        self.update_kb_and_cell_prob(percepts)

        if len(self.route) == 0:
            safe_nv_cell, safe_nv_route = self.get_nearest_notvisited_safe_cell_route()
            if safe_nv_cell is not None:
                self.route = safe_nv_route
                if self.debug:
                    print(f"[DEBUG] Nearest not visited safe cell: {safe_nv_cell}. Advancing there, found route: {self.route}.")
            elif self.can_hunt and self.can_shoot:
                if self.debug:
                    print("[DEBUG] Can hunt and shoot. Finding shoot path.")
                hunt_plan = self.find_shoot_path()
                if hunt_plan is not None:
                    if self.debug:
                        print(f"Found hunt path. Moving to hunt spot: {hunt_plan}")
                    while (len(hunt_plan) > 0):
                        self.move_to_pos(hunt_plan[0])
                        hunt_plan = hunt_plan[1:]
                    if self.debug:
                        print(f"[DEBUG] Aimed Wumpus at {self.aimed_wumpus}. Turning to shoot direction.")
                    shoot = self.turn_to_shoot_dir()
                    if not shoot:
                        print("Tinh sai vi tri ban roi m")
                    wumpus_die = self.shoot()
                    if wumpus_die:
                        if self.debug:
                            print(f"[DEBUG] Wumpus at {self.aimed_wumpus} killed. Updating KB and probabilities.")
                        self.wumpus_at.remove(self.aimed_wumpus)
                        self.wumpus_prob[self.aimed_wumpus] = 0
                        self.cell_prob[self.aimed_wumpus] = 0
                        self.kb.add_fact(f"!Wumpus({self.x}, {self.y})")
                        self.pm.add_safe_cell(self.aimed_wumpus)
                return True
            else:
                if self.debug:  
                    print(f"[DEBUG] Uncertain cells: {self.uncertain_cell.heap}")
                goal, die_prob = self.uncertain_cell.popitem()
                if self.debug:
                    print(f"[DEBUG] No safe route. Popping cell {goal} with die_prob {die_prob}.")
                if (die_prob < 0.8):
                    self.pm.space.add(goal)
                    result,_ = self.pm.find_route((self.x, self.y),goal, self.dir)
                    self.route = result
                    print(f"[DEBUG] Start: {(self.x, self.y)} Found route to uncertain cell {goal}: {result}.")
        else:
            if self.debug:
                print(f"[DEBUG] Route available: {self.route}. Moving to next position.")

        if (len(self.route) > 0):
            cur_pos = (self.x, self.y)
            if self.debug:
                print(f"[DEBUG] Moving to position {self.route[0]}. Marking as visited.")
            self.move_to_pos(self.route[0])
            self.visited.add(self.route[0])
            self.route = self.route[1:]
            if self.debug:
                print("[DEBUG] Step completed. Returning True.")
            return True
        else:
            self.route,_ = self.pm.find_route((self.x, self.y),(0,0),self.dir)
            self.to_climbout = True
            if self.debug:
                print("[DEBUG] No route available. Climbing out.")
            
            return False


if __name__ == "__main__":
    pass