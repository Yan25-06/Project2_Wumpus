from ..agents.hybrid_agent import HybridAgent
from ..ai.knowledge_base import KnowledgeBase
from ..ai.inference_engine import InferenceEngine
from ..ai.planning_module import PlanningModule 
from ..core.environment import Environment
import pickle
import os


def init_agent(map_path = None, debug = False):
    kb = KnowledgeBase()
    ie = InferenceEngine(kb)
    pm = PlanningModule()
    if map_path is None:
        env = Environment()
    else:
        with open(map_path, "rb") as f:
            env = pickle.load(f)
    agent = HybridAgent(env, kb, ie, pm, debug)

    agent.x = 0
    agent.y = 0
    agent.route = [] 
    agent.visited = {(0, 0)}  # Start with the initial position as visited

    return agent

def test_kb_initialization():
    agent = init_agent()
    assert len(agent.kb.get_facts()) > 0, "Facts not loaded into KB"
    assert len(agent.kb.get_rules()) > 0, "Rules not loaded into KB"
    print("test_kb_initialization passed.")


def test_update_kb_and_cell_prob():
    agent = init_agent()
    percepts = {'stench': True, 'breeze': True, 'glitter': False}
    agent.x, agent.y = 1, 1
    agent.update_kb_and_cell_prob(percepts)
    assert hasattr(agent, 'cell_prob'), "cell_prob not updated"
    print("test_update_kb_and_cell_prob passed.")


def test_add_adj_as_safe_cell():
    agent = init_agent()
    agent.x, agent.y = 2, 2
    agent.cell_prob = {}
    agent.pm.space = set()
    agent.add_adj_as_safe_cell()
    adj = [(3,2), (1,2), (2,3), (2,1)]
    for cell in adj:
        assert agent.cell_prob[cell] == 0, f"Cell {cell} not marked safe"
    print("test_add_adj_as_safe_cell passed.")


def test_get_nearest_notvisited_safe_cell():
    agent = init_agent()
    agent.x, agent.y = 0, 0
    agent.pm.space = {(1,0), (0,1), (2,2)}
    agent.visited = {(0,0), (1,0)}
    cell = agent.get_nearest_notvisited_safe_cell()
    assert cell == (0,1), f"Expected (0,1), got {cell}"
    print("test_get_nearest_notvisited_safe_cell passed.")


def test_find_shoot_path():
    agent = init_agent()
    agent.x, agent.y = 0, 0
    agent.pm.space = {(0,0), (1,0), (2,0), (2,2)}
    agent.wumpus_at = [(2,0)]
    path = agent.find_shoot_path()
    assert path is not None, "No shoot path found"
    print("test_find_shoot_path passed.")

    return agent
def test_step(agent:HybridAgent):
    # step return True or False 
    print("Initial environment state:")
    agent.env.print_environment_state()
    result = agent.step()

    print(f"Step result: {result}")
    assert result is True or result is False, "Step did not return a boolean"
    print("test_step passed.")
    return agent, result


def test_find_route_from_A_to_B():
    pm = PlanningModule()
    # Define a simple space: 3x3 grid, all cells are safe
    pm.space = {(x, y) for x in range(5) for y in range(5)}
    start = (0, 0)
    goal = (1, 0)
    start_dir = 'E'  # Assume 'E' is a valid direction
    route = pm.find_route(start, goal, start_dir)
    print(f"Route from {start} to {goal} (start_dir={start_dir}):")
    print(route)
    # expected_route = [(1,0), (2,0), (3,0), (4,0), (4,1), (4,2), (4,3), (4,4)] 
    expected_route = [(1,0)] 
    assert route == expected_route, f"Expected {expected_route}, got {route}"
    print("test_find_route_from_A_to_B passed.")


def main():
    path = "saved_envs/comfy_map.pkl"
    a = init_agent(path, debug=True)
    try: 
        a, res = test_step(a)  
        step = 1
        while res and step <= 30:
            a, res = test_step(a)
            step += 1
    except Exception as e:
        print(f"An error occurred during the test: {e}")
        # print whole traceback
        import traceback
        traceback.print_exc()
        return
    finally: 
        # Prompt to save environment after each run
        save_prompt = input("Do you want to save the environment? (y/n): ").strip().lower()
        if save_prompt == 'y':
            folder = "saved_envs"
            os.makedirs(folder, exist_ok=True)
            filename = input("Enter filename for environment (without extension): ").strip()
            filepath = os.path.join(folder, f"{filename}.pkl")
            with open(filepath, "wb") as f:
                pickle.dump(a.env, f)
            print(f"Environment saved to {filepath}")

if __name__ == "__main__":
    main()
    # test_find_route_from_A_to_B()
