import random

class Cell:
    def __init__(self):
        self.has_wumpus = False
        self.has_pit = False
        self.has_gold = False
        self.visited = False
        self.safe = None  # True / False / None (unknown)
        self.percepts = {'stench': False, 'breeze': False, 'glitter': False}  # Store percepts when visited

class Environment:
    def __init__(self, N=8, K=2, pit_prob=0.2, seed=None):
        self._rand = random.Random(seed + pit_prob * 10 - N / 2) if seed is not None else random.Random()

        print(seed)
        self.__N = N
        self.__grid = [[Cell() for _ in range(N)] for _ in range(N)]
        self.__agent_pos = (0, 0)
        self.__agent_dir = 'E'  # E, N, W, S
        self.__scream = False
        self.__wumpus = K

        self.__place_pits(pit_prob)
        self.__place_wumpus(K)
        self.__place_gold()

    # Randomly place pits based on probability
    def __place_pits(self, pit_prob):
        for y in range(self.__N):
            for x in range(self.__N):
                if (x, y) == (0, 0): continue
                if self._rand.random() < pit_prob:
                    self.__grid[y][x].has_pit = True

    # Randomly place Wumpus
    # Ensure at least K Wumpuses are placed, not in (0, 0)
    def __place_wumpus(self, K):
        placed = 0
        while placed < K:
            x = self._rand.randint(0, self.__N - 1)
            y = self._rand.randint(0, self.__N - 1)
            if (x, y) != (0, 0) and not self.__grid[y][x].has_pit and not self.__grid[y][x].has_wumpus:
                self.__grid[y][x].has_wumpus = True
                placed += 1

    # Randomly place gold
    def __place_gold(self):
        while True:
            x = self._rand.randint(0, self.__N - 1)
            y = self._rand.randint(0, self.__N - 1)
            if not self.__grid[y][x].has_pit and not self.__grid[y][x].has_wumpus:
                self.__grid[y][x].has_gold = True
                self.__gold_pos = (x, y)
                break

    def get_agent_pos(self):
        return self.__agent_pos
    def get_agent_dir(self):
        return self.__agent_dir
    def get_scream(self):
        return self.__scream
    
    def reset_scream(self):
        self.__scream = False
        
    def get_size(self):
        return self.__N
    

    def shot_wumpus(self):
        dx, dy = 0, 0
        if self.__agent_dir == 'N':
            dy = 1
        elif self.__agent_dir == 'S':
            dy = -1
        elif self.__agent_dir == 'E':
            dx = 1
        elif self.__agent_dir == 'W':
            dx = -1

        for step in range(1, self.__N):
            x, y = self.__agent_pos
            nx, ny = x + dx * step, y + dy * step
            if 0 <= nx < self.__N and 0 <= ny < self.__N:
                if self.has_wumpus(nx, ny):
                    self.__scream = True
                    self.__wumpus -= 1
                    # Remove the Wumpus from the grid
                    self.__grid[ny][nx].has_wumpus = False
                    return True
        return False
    def grabbed_gold(self):
        x, y = self.__gold_pos
        self.__grid[y][x].has_gold = False

    def set_agent_pos_and_dir(self, x, y, direction):
        if 0 <= x < self.__N and 0 <= y < self.__N:
            self.__agent_pos = (x, y)
            self.__agent_dir = direction
        else:
            raise ValueError("Agent position out of bounds")
        
    def set_safe(self, x, y):
        self.__grid[y][x].safe = True
    def set_dangerous(self, x, y):
        self.__grid[y][x].safe = False

    def has_pit(self, x, y):
        if 0 <= x < self.__N and 0 <= y < self.__N:
            return self.__grid[y][x].has_pit
        return False
    def has_wumpus(self, x, y):
        if 0 <= x < self.__N and 0 <= y < self.__N:
            return self.__grid[y][x].has_wumpus
        return False
    
    def has_gold(self, x, y):
        if 0 <= x < self.__N and 0 <= y < self.__N:
            return self.__grid[y][x].has_gold
        return False
    
    def is_visited(self, x, y):
        if 0 <= x < self.__N and 0 <= y < self.__N:
            return self.__grid[y][x].visited
        return False
    
    def mark_visited(self, x, y):
        if 0 <= x < self.__N and 0 <= y < self.__N:
            self.__grid[y][x].visited = True
            # Store percepts for this cell when visited
            percepts = self.get_percepts(x, y)
            self.__grid[y][x].percepts = percepts
    
    def reset_visited_cells(self):
        """Reset all visited markers in the environment and restore gold to original position"""
        for y in range(self.__N):
            for x in range(self.__N):
                self.__grid[y][x].visited = False
                self.__grid[y][x].percepts = {'stench': False, 'breeze': False, 'glitter': False}
        
        # Restore gold to its original position if it was grabbed
        if hasattr(self, '_Environment__gold_pos'):
            gold_x, gold_y = self.__gold_pos
            self.__grid[gold_y][gold_x].has_gold = True
    
    def get_cell_percepts(self, x, y):
        """Get the stored percepts for a visited cell"""
        if 0 <= x < self.__N and 0 <= y < self.__N and self.__grid[y][x].visited:
            return self.__grid[y][x].percepts
        return {'stench': False, 'breeze': False, 'glitter': False}
    
    def get_percepts(self, x, y):
        stench = breeze = glitter = False
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.__N and 0 <= ny < self.__N:
                if self.__grid[ny][nx].has_wumpus:
                    stench = True
                if self.__grid[ny][nx].has_pit:
                    breeze = True
        glitter = self.__grid[y][x].has_gold
        return {'stench': stench, 'breeze': breeze, 'glitter': glitter}
    
    def print_environment_state(self):
        print(f"Grid size: {self.__N}x{self.__N}")
        print(f"Agent position: {self.__agent_pos}, direction: {self.__agent_dir}")
        print(f"Scream: {self.__scream}")
        print(f"Wumpus remaining: {self.__wumpus}")
        print("Grid:")
        for y in range(self.__N):
            row = []
            for x in range(self.__N):
                cell = self.__grid[y][x]
                cell_str = ""
                if cell.has_wumpus:
                    cell_str += "W"
                if cell.has_pit:
                    cell_str += "P"
                if cell.has_gold:
                    cell_str += "G"
                # Pad or trim to 3 characters
                cell_str = cell_str[:3].ljust(3)
                if cell_str.strip() == "":
                    cell_str = ".  "
                row.append(cell_str)
            print(" ".join(row))


