import random
from ..agents.agent import Agent

# Random Agent for Wumpus World
# This agent makes random decisions based on the current state of the environment.
# Use for testing or as a baseline agent.
class RandomAgent(Agent):
    def __init__(self, env):
        super().__init__(env)
        self.is_turn = False
    def step(self):
        if not self.alive:
            return False
        percept = self.env.get_percepts(self.x, self.y)
        if percept['glitter']:
            self.grab_gold()
            return True
        if percept['stench']:
            if not self.is_turn:
                action = random.choice(['turn_left', 'turn_right', 'move'])
                if action == 'turn_left':
                    self.is_turn = True
                    self.turn_left()
                elif action == 'turn_right':
                    self.is_turn = True
                    self.turn_right()
                elif action == 'move':
                    self.move_forward()
            else:
                self.is_turn = False
                self.shoot()
            return True
        if percept['breeze']:
            if not self.is_turn:
                action = random.choice(['turn_left', 'turn_right', 'move'])
                if action == 'turn_left':
                    self.is_turn = True
                    self.turn_left()
                elif action == 'turn_right':
                    self.is_turn = True
                    self.turn_right()
                elif action == 'move':
                    self.move_forward()
            else:
                self.is_turn = False
                self.move_forward()
            return True

        if(self.x, self.y) == (0, 0):
            action = random.choice(['move', 'move', 'move', 'move', 'move', 'move', 'move', 'move', 'turn_left', 'turn_right', 'climb_out'])
        else:
            action = random.choice(['move', 'move', 'move', 'move', 'move', 'move', 'move', 'move', 'turn_left', 'turn_right'])
        if action == 'move':
            self.move_forward()
        elif action == 'turn_left':
            self.turn_left()
        elif action == 'turn_right':
            self.turn_right()
        elif action == 'climb_out':
            self.climb_out()
            return False
        return True
