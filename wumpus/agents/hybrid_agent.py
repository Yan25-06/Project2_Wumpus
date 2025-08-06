from ..agents.agent import Agent

class HybridAgent(Agent):
    def __init__(self, env):
        super().__init__(env)
     

    def step(self):
        if not self.alive:
            return False
        if self.grab_gold():
            return True
        # Kết hợp inference engine và planning module
        return True