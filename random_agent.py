import random
from agent import Agent

class RandomAgent(Agent):
    def step(self):
        if not self.alive:
            return False
        if self.grab_gold():
            return True
        self.visited.add((self.x, self.y))
        if(self.x, self.y) == (0, 0):
            action = random.choice(['move', 'turn_left', 'turn_right', 'climb_out', 'shoot'])
        else:
            action = random.choice(['move', 'turn_left', 'turn_right', 'shoot'])
        if action == 'move':
            self.move_forward()
        elif action == 'turn_left':
            self.turn_left()
        elif action == 'turn_right':
            self.turn_right()
        elif action == 'climb_out':
            return self.climb_out()
        elif action == 'shoot':
            self.shoot()
        return True
