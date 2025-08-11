import random
from ..agents.agent import Agent

# Random Agent for Wumpus World
# This agent makes random decisions based on the current state of the environment.
# Use for testing or as a baseline agent.
class RandomAgent(Agent):
    def step(self):
        if not self.alive:
            return False
        percept = self.env.get_percepts(self.x, self.y)
        if percept['glitter']:
            self.grab_gold()
            return True
        if(self.x, self.y) == (0, 0):
            action = random.choice(['move', 'move', 'turn_left', 'turn_right', 'climb_out', 'shoot'])
        else:
            action = random.choice(['move', 'move', 'turn_left', 'turn_right', 'shoot'])
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
