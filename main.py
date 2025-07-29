from environment import Environment
from random_agent import RandomAgent

env = Environment(N=4)
agent = RandomAgent(env)

steps = 0
while agent.step():
    steps += 1
    if steps > 100:
        print("Agent took too long!")
        break

print(f"Final Score: {agent.score}")


