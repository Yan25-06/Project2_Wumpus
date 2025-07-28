import random

class RandomAgent:
    def __init__(self, env):
        self.env = env
        self.x, self.y = env.agent_pos
        self.dir = env.agent_dir
        self.has_gold = False
        self.alive = True
        self.score = 0
        self.visited = set()

    def step(self):
        if not self.alive:
            return False

        self.visited.add((self.x, self.y))
        percepts = self.env.get_percepts(self.x, self.y)
        print(f"Agent at ({self.x},{self.y}) | Percepts: {percepts} | Score: {self.score}")

        if percepts['glitter']:
            self.has_gold = True
            self.score += 10
            self.env.grid[self.y][self.x].has_gold = False
            print("Agent grabbed the gold!")

        if self.has_gold and (self.x, self.y) == (0, 0):
            self.score += 1000
            print("Agent climbed out with the gold!")
            return False  # End

        move = random.choice(['forward', 'left', 'right'])
        if move == 'left':
            self.turn_left()
        elif move == 'right':
            self.turn_right()
        elif move == 'forward':
            self.move_forward()
        return True

    def turn_left(self):
        dirs = ['N', 'W', 'S', 'E']
        self.dir = dirs[(dirs.index(self.dir) + 1) % 4]
        self.score -= 1
        print(f"Agent turned left to {self.dir}")

    def turn_right(self):
        dirs = ['N', 'E', 'S', 'W']
        self.dir = dirs[(dirs.index(self.dir) + 1) % 4]
        self.score -= 1
        print(f"Agent turned right to {self.dir}")


    def move_forward(self):
        dx, dy = {'N':(0,1), 'E':(1,0), 'S':(0,-1), 'W':(-1,0)}[self.dir]
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < self.env.N and 0 <= ny < self.env.N:
            self.x, self.y = nx, ny
            self.score -= 1
            cell = self.env.grid[self.y][self.x]
            if cell.has_pit or cell.has_wumpus:
                print("Agent died!")
                self.alive = False
                self.score -= 1000
        else:
            print("Bump!")
            self.score -= 1
