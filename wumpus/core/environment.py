import random

class Cell:
    def __init__(self):
        self.has_wumpus = False
        self.has_pit = False
        self.has_gold = False
        self.visited = False
        self.safe = None  # True / False / None (unknown)

class Environment:
    def __init__(self, N=8, K=2, pit_prob=0.2):
        self.N = N
        self.grid = [[Cell() for _ in range(N)] for _ in range(N)]
        self.agent_pos = (0, 0)
        self.agent_dir = 'E'  # E, N, W, S
        self.scream = False
        self.wumpus = K

        self.place_pits(pit_prob)
        self.place_wumpus(K)
        self.place_gold()

    # Randomly place pits based on probability
    def place_pits(self, pit_prob):
        for y in range(self.N):
            for x in range(self.N):
                if (x, y) == (0, 0): continue
                if random.random() < pit_prob:
                    self.grid[y][x].has_pit = True

    # Randomly place Wumpus
    # Ensure at least K Wumpuses are placed, not in (0, 0)
    def place_wumpus(self, K):
        placed = 0
        while placed < K:
            x = random.randint(0, self.N - 1)
            y = random.randint(0, self.N - 1)
            if (x, y) != (0, 0) and not self.grid[y][x].has_pit and not self.grid[y][x].has_wumpus:
                self.grid[y][x].has_wumpus = True
                placed += 1

    # Randomly place gold
    def place_gold(self):
        while True:
            x = random.randint(0, self.N - 1)
            y = random.randint(0, self.N - 1)
            if not self.grid[y][x].has_pit and not self.grid[y][x].has_wumpus:
                self.grid[y][x].has_gold = True
                break

    def get_percepts(self, x, y):
        stench = breeze = glitter = False
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.N and 0 <= ny < self.N:
                if self.grid[ny][nx].has_wumpus:
                    stench = True
                if self.grid[ny][nx].has_pit:
                    breeze = True
        glitter = self.grid[y][x].has_gold
        return {'stench': stench, 'breeze': breeze, 'glitter': glitter}
