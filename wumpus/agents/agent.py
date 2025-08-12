from abc import ABC, abstractmethod
from ..core.environment import Environment
from ..config.settings import DIRECTIONS, DIRECTION_VECTORS
# Agent base class for Wumpus World
# This class defines the basic structure and methods that all agents must implement.
class Agent(ABC):
    def __init__(self, env: Environment):
        self.env = env
        self.x, self.y = env.get_agent_pos()
        self.dir = env.get_agent_dir()
        self.has_gold = False
        self.can_shoot = True
        self.alive = True
        self.score = 0
        # Mark starting position as visited
        self.env.mark_visited(self.x, self.y)

    @abstractmethod
    def step(self) -> bool:
        """Perform one step of the agent's action."""
        pass

    def turn_left(self):
        dirs = ['N', 'E', 'S', 'W']
        self.dir = dirs[(dirs.index(self.dir) - 1) % 4]
        self.env.set_agent_pos_and_dir(self.x, self.y, self.dir)
        self.score -= 1
        print(f"Agent turned left to {self.dir}")

    def turn_right(self):
        dirs = ['N', 'E', 'S', 'W']
        self.dir = dirs[(dirs.index(self.dir) + 1) % 4]
        self.env.set_agent_pos_and_dir(self.x, self.y, self.dir)
        self.score -= 1
        print(f"Agent turned right to {self.dir}")


    def move_forward(self):
        dx, dy = {'N':(0,1), 'E':(1,0), 'S':(0,-1), 'W':(-1,0)}[self.dir]
        nx, ny = self.x + dx, self.y + dy
        self.score -= 1
        if 0 <= nx < self.env.get_size() and 0 <= ny < self.env.get_size():
            self.x, self.y = nx, ny
            self.env.set_agent_pos_and_dir(self.x, self.y, self.dir)
            self.env.mark_visited(self.x, self.y)  # Mark new cell as visited
            print(f"Agent moved to ({self.x}, {self.y}) facing {self.dir}")
            if self.env.has_pit(self.x, self.y) or self.env.has_wumpus(self.x, self.y):
                print("Agent died!")
                self.alive = False
                self.score -= 1000
        else:
            print("Bump!")
    
    def move_to_pos(self, pos):
        pos_x, pos_y = pos
        dx = pos_x - self.x
        dy = pos_y - self.y
        if (dx, dy) not in DIRECTION_VECTORS:
            if (dx, dy) == (0,0):
                print("Same spot")
                return
            else:
                raise ValueError("Can only move to adjacent cell.")
        dir = DIRECTION_VECTORS[(dx, dy)]
        diff = (DIRECTIONS.index(dir) - DIRECTIONS.index(self.dir)) % 4

        if diff == 1:
            self.turn_right()
        elif diff == 2:
            self.turn_right()
            self.turn_right()
        elif diff == 3:
            self.turn_left()
        
        self.move_forward()

    def grab_gold(self):
        self.has_gold = True
        self.score += 10
        self.env.grabbed_gold()
        self.env.set_safe(self.x, self.y)
        print("Agent grabbed the gold!")
    
    def climb_out(self):
        if self.has_gold:
            self.score += 1000
            print("Agent climbed out with the gold!")
        else:
            print("Agent climbed out without gold.")
    
    def shoot(self):
        if not self.can_shoot:
            print("Agent cannot shoot again yet!")
            return False
        self.score -= 10
        self.can_shoot = False
        
        if self.env.shot_wumpus():
            print("Agent killed the Wumpus!")
            return True
        else:
            print("Agent shot but missed.")
            return False
