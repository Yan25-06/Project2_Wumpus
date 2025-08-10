from ..agents.agent import Agent
from ..ai.inference_engine import InferenceEngine, KnowledgeBase
from ..ai.planning_module import PlanningModule
from heapdict import heapdict
from heapq import heappush, heappop
from ..config.settings import DIRECTIONS, DIRECTION_VECTORS

class HybridAgent(Agent):


    def init_kb(self,kb: KnowledgeBase):

        # init kb 
        self.kb = kb
        try: 
            # read rules from rules.txt file in cwd
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

    def __init__(self, env, kb: KnowledgeBase, ie: InferenceEngine, pm: PlanningModule):
        super().__init__(env)

        self.init_kb(kb)
        

        self.ie = ie
        self.pm = pm

        self.can_hunt = False
        self.aimed_wumpus = (-1, -1)

        self.visited = set()
        self.route = []

        self.wumpus_at = []
        self.wumpus_prob: dict[tuple, float]
        self.pit_prob: dict[tuple, float]
        self.cell_prob = heapdict() # 0: safe 1: die

    def update_kb_and_cell_prob(self,percepts):
        adj = [(self.x+1, self.y), (self.x-1, self.y), (self.x, self.y+1), (self.x, self.y-1)]
        if (percepts["stench"]):
            self.kb.update_kb(f"Stench({self.x}, {self.y})")
            for cell in adj:
                if (cell not in self.cell_prob or (self.cell_prob[cell] > 0 and self.cell_prob[cell] < 1)):
                    self.wumpus_prob[cell] = self.ie.model_check_probability(f"Wumpus({self.x}, {self.y})")
                    if self.wumpus_prob[cell] == 1:
                        self.can_hunt = True
                        if cell not in self.wumpus_at:
                            self.wumpus_at.append(cell)

        if (percepts["breeze"]):
            self.kb.update_kb(f"Breeze({self.x}, {self.y})")
            for cell in adj:
                if (cell not in self.cell_prob or 0 < self.cell_prob[cell] < 1):
                    self.pit_prob[cell] = self.ie.model_check_probability(f"Pit({self.x}, {self.y})")

        for cell in adj:
            if (cell in self.wumpus_prob and cell in self.pit_prob):
                self.cell_prob[cell] = 1 - (1 - self.wumpus_prob[cell]) * (1 - self.pit_prob[cell])
            elif (cell in self.wumpus_prob):
                self.cell_prob[cell] = self.wumpus_prob[cell]
            elif (cell in self.pit_prob):
                self.cell_prob[cell] = self.pit_prob[cell]
            if (self.cell_prob[cell] == 0):
                self.pm.add_safe_cell(cell)

    def add_adj_as_safe_cell(self):
        adj = [(self.x+1, self.y), (self.x-1, self.y), (self.x, self.y+1), (self.x, self.y-1)]
        for cell in adj:
            if (cell not in self.cell_prob or 0 < self.cell_prob[cell] < 1):
                self.cell_prob[cell] = 0
                self.pm.add_safe_cell(cell)

    def get_nearest_notvisited_safe_cell(self):
        current_pos = (self.x, self.y)
        candidates = [cell for cell in self.pm.space if cell not in self.visited]
        if not candidates:
            return None
        return min(candidates, key=lambda cell: abs(cell[0] - current_pos[0]) + abs(cell[1] - current_pos[1]))

    def find_shoot_path(self):
        current_pos = (self.x, self.y)

        sorted_wumpus = sorted(self.wumpus_at, key=lambda w: self.pm.heuristic(w, current_pos))

        for wumpus in sorted_wumpus:
            self.aimed_wumpus = wumpus
            wx, wy = wumpus
            shoot_candidates = []
            n = self.env.get_size()
            for x in range(n):  
                if (x, wy) in self.pm.space and (x, wy) != wumpus:
                    heappush(shoot_candidates, (self.pm.heuristic(current_pos, (x, wy)), (x, wy)))

            for y in range(n):
                if (wx, y) in self.pm.space and (wx, y) != wumpus:
                    heappush(shoot_candidates, (self.pm.heuristic(current_pos, (wx, y)), (wx, y)))

            while shoot_candidates:
                shoot_pos,_ = heappop(shoot_candidates)
                path = self.pm.find_route((self.x, self.y), shoot_pos, self.dir)
                if path: 
                    return path

        return None  

    def turn_to_shoot_dir(self):
        wx, wy = self.aimed_wumpus
        ax, ay = self.x, self.y

        if ax == wx:
            if wy > ay:
                target_dir = 'E'
            else:
                target_dir = 'W'
        elif ay == wy:
            if wx > ax:
                target_dir = 'S'
            else:
                target_dir = 'N'
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
            return False
        percepts = self.env.get_percepts()
        if percepts["glitter"]:
            self.grab_gold()
            self.route = self.pm.find_route((0,0))
        if self.has_gold and self.x == 0 and self.y == 0: # has gold and at exit
            return False
        if not percepts["stench"] and not percepts["breeze"]:
            self.add_adj_as_safe_cell()
        else:
            self.update_kb_and_cell_prob(percepts)
        if len(self.route == 0):
            if self.aimed_wumpus != (-1, -1):
                shoot = self.turn_to_shoot_dir()
                if not shoot:
                    print("Tinh sai vi tri ban roi m")
                wumpus_die = self.shoot()
                if wumpus_die:
                    self.wumpus_at.remove(self.aimed_wumpus)
                    self.wumpus_prob[self.aimed_wumpus] = 0
                    self.cell_prob[self.aimed_wumpus] = 0
                    self.kb.add_fact(f"!Wumpus({self.x}, {self.y})")
                    self.pm.add_safe_cell(self.aimed_wumpus)
                self.aimed_wumpus = (-1, -1)
            cell = self.get_nearest_notvisited_safe_cell()
            if cell:
                self.route = self.pm.find_route((self.x, self.y), cell, self.dir)
            elif self.can_hunt and self.can_shoot:
                hunt_plan = self.find_shoot_path()
                if len(hunt_plan) > 0:
                    self.route = hunt_plan
            else:
                goal, die_prob = self.cell_prob.popitem()
                if (die_prob < 1):
                    self.route = self.pm.find_route(goal)
        if (len(self.route) > 0):
            self.move_to_pos(self.route[0])
            self.visited.add(self.route[0])
            self.route = self.route[:1]
            return True
        else:
            return False


if __name__ == "__main__":
    pass 