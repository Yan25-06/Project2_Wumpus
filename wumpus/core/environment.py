import random

class Cell:
    def __init__(self):
        self.has_wumpus = False
        self.has_pit = False
        self.has_gold = False
        self.safe = None  # True / False / None (unknown)

class Environment:
    def __init__(self, N=8, K=2, pit_prob=0.2):
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
                if random.random() < pit_prob:
                    self.__grid[y][x].has_pit = True

    # Randomly place Wumpus
    # Ensure at least K Wumpuses are placed, not in (0, 0)
    def __place_wumpus(self, K):
        placed = 0
        while placed < K:
            x = random.randint(0, self.__N - 1)
            y = random.randint(0, self.__N - 1)
            if (x, y) != (0, 0) and not self.__grid[y][x].has_pit and not self.__grid[y][x].has_wumpus:
                self.__grid[y][x].has_wumpus = True
                placed += 1

    # Randomly place gold
    def __place_gold(self):
        while True:
            x = random.randint(0, self.__N - 1)
            y = random.randint(0, self.__N - 1)
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
    def get_size(self):
        return self.__N
    

    def shot_wumpus(self):
        dx, dy = 0, 0
        if self.__agent_dir == 'N':
            dy = -1
        elif self.__agent_dir == 'S':
            dy = 1
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
