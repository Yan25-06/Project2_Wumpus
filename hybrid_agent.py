from agent import Agent

class HybridAgent(Agent):
    def step(self):
        if not self.alive:
            return False
        if self.grab_gold():
            return True
        # Kết hợp inference engine và planning module
        return True