from Project2_Wumpus.wumpus.core.environment import Environment
from Project2_Wumpus.wumpus.agents.random_agent import RandomAgent

env = Environment(N=4)
agent = RandomAgent(env)

steps = 0
while agent.step():
    steps += 1
    if steps > 100:
        print("Agent took too long!")
        break

print(f"Final Score: {agent.score}")


