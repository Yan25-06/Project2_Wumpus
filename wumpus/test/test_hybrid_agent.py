from ..agents.hybrid_agent import HybridAgent
from ..ai.knowledge_base import KnowledgeBase
from ..ai.inference_engine import InferenceEngine
from ..ai.planning_module import PlanningModule 
from ..core.environment import Environment


def init_agent():
    kb = KnowledgeBase()
    ie = InferenceEngine(kb)
    pm = PlanningModule()
    env = Environment()
    agent = HybridAgent(env, kb, ie, pm)
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


def test_step():
    agent = init_agent()
    agent.x, agent.y = 0, 0
    agent.env.get_percepts = lambda: {'stench': False, 'breeze': False, 'glitter': False}
    agent.route = []
    agent.pm.space = {(1,0), (0,1)}
    agent.visited = {(0,0)}
    result = agent.step()
    assert result is True or result is False, "Step did not return a boolean"
    print("test_step passed.")


if __name__ == "__main__":
    test_step()
    pass 
