from abc import ABC, abstractmethod

# Agent base class for Wumpus World
# This class defines the basic structure and methods that all agents must implement.
class Agent(ABC):
    def __init__(self, env):
        self.env = env
        self.x, self.y = env.agent_pos
        self.dir = env.agent_dir
        self.has_gold = False
        self.can_shoot = True
        self.alive = True
        self.score = 0
        self.visited = set()

    @abstractmethod
    def step(self) -> bool:
        """Perform one step of the agent's action."""
        pass

    def turn_left(self):
        dirs = ['N', 'W', 'S', 'E']
        self.dir = dirs[(dirs.index(self.dir) + 1) % 4]
        self.env.agent_dir = self.dir
        self.score -= 1
        print(f"Agent turned left to {self.dir}")

    def turn_right(self):
        dirs = ['N', 'E', 'S', 'W']
        self.dir = dirs[(dirs.index(self.dir) + 1) % 4]
        self.env.agent_dir = self.dir
        self.score -= 1
        print(f"Agent turned right to {self.dir}")


    def move_forward(self):
        dx, dy = {'N':(0,1), 'E':(1,0), 'S':(0,-1), 'W':(-1,0)}[self.dir]
        nx, ny = self.x + dx, self.y + dy
        self.score -= 1
        if 0 <= nx < self.env.N and 0 <= ny < self.env.N:
            self.x, self.y = nx, ny
            self.env.agent_pos = (self.x, self.y) # Update the environment's agent position
            cell = self.env.grid[self.y][self.x]
            cell.visited = True
            print(f"Agent moved to ({self.x}, {self.y}) facing {self.dir}")
            if cell.has_pit or cell.has_wumpus:
                print("Agent died!")
                self.alive = False
                self.score -= 1000
        else:
            print("Bump!")
    
    def grab_gold(self):
        percept = self.env.get_percepts(self.x, self.y)
        if percept['glitter']:
            self.has_gold = True
            self.score += 10
            self.env.grid[self.y][self.x].has_gold = False
            self.env.grid[self.y][self.x].safe = True
            print("Agent grabbed the gold!")
            return True
        return False
    
    def climb_out(self):
        if self.has_gold:
            self.score += 1000
            print("Agent climbed out with the gold!")
        else:
            print("Agent climbed out without gold.")
    
    def shoot(self):
        if not self.can_shoot:
            print("Agent cannot shoot again yet!")
            return
        self.score -= 10
        self.can_shoot = False
        dx, dy = 0, 0
        if self.dir == 'N':
            dy = -1
        elif self.dir == 'S':
            dy = 1
        elif self.dir == 'E':
            dx = 1
        elif self.dir == 'W':
            dx = -1

        for step in range(1, self.env.N):
            nx, ny = self.x + dx * step, self.y + dy * step
            if 0 <= nx < self.env.N and 0 <= ny < self.env.N:
                cell = self.env.grid[ny][nx]
                if cell.has_wumpus:
                    cell.has_wumpus = False
                    self.env.scream = True
                    self.env.wumpus -= 1
                    print("Agent killed the Wumpus!")
        if not self.env.scream:            
            print("Agent shot but missed.")
