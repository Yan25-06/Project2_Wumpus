from .core.environment import Environment
from .agents.random_agent import RandomAgent
from .ai.planning_module import PlanningModule
env = Environment(N=4)
agent = RandomAgent(env)
safe_cell = [(x, y) for x in range(4) for y in range(4)]
plan = PlanningModule(safe_cell, env.agent_pos, env.agent_dir)

route = plan.find_route((0,3))
print(route)

# steps = 0
# # while agent.step():
# #     steps += 1
# #     if steps > 100:
# #         print("Agent took too long!")
# #         break

# print(f"Final Score: {agent.score}")


