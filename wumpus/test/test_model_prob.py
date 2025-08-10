from ..ai.knowledge_base import KnowledgeBase 
from ..ai.inference_engine import InferenceEngine

def init_ie():
    kb = KnowledgeBase()
    engine = InferenceEngine(kb)

    # read rules.txt
    with open("rules.txt", "r") as f:
        for line in f:
            engine.kb.add_rule(line.strip())
    # read facts.txt
    with open("facts.txt", "r") as f:
        for line in f:
            engine.kb.add_fact(line.strip())
    return engine

def test_model_check_probability_1():
    ie = init_ie()
    kb = ie.kb
    kb.add_fact("Breeze(1,1)")

    probability = ie.model_check_probability("Pit(1,2)")
    print(f"Probability of 'Pit(1,2)' being true: {probability}") # 0.5333

def test_model_check_probability_2():
    ie = init_ie()
    kb = ie.kb
    kb.add_fact("Breeze(2,2)")
    probability = ie.model_check_probability("Pit(2,3)")
    print(f"Probability of 'Pit(2,3)' being true: {probability}")


def test_model_check_probability_3():
    ie = init_ie()
    kb = ie.kb
    kb.add_fact("Stench(1,1)")
    probability = ie.model_check_probability("Wumpus(1,2)")
    print(f"Probability of 'Wumpus(1,2)' being true: {probability}")


def test_model_check_probability_4():
    ie = init_ie()
    kb = ie.kb
    kb.add_fact("!Breeze(1,1)")
    probability = ie.model_check_probability("Pit(1,2)")
    print(f"Probability of 'Pit(1,2)' being true: {probability}")


def test_model_check_probability_5():
    ie = init_ie()
    kb = ie.kb
    kb.add_fact("!Stench(2,2)")
    probability = ie.model_check_probability("Wumpus(2,3)")
    print(f"Probability of 'Wumpus(2,3)' being true: {probability}")


def test_model_check_probability_6():
    ie = init_ie()
    kb = ie.kb
    kb.add_fact("Breeze(1,1)")
    kb.add_fact("Stench(1,1)")
    probability_pit = ie.model_check_probability("Pit(1,2)")
    probability_wumpus = ie.model_check_probability("Wumpus(1,2)")
    print(f"Probability of 'Pit(1,2)' being true: {probability_pit}")
    print(f"Probability of 'Wumpus(1,2)' being true: {probability_wumpus}")


def test_model_check_probability_multiple_breeze():
    ie = init_ie()
    kb = ie.kb
    # Add multiple Breeze facts in different locations
    kb.add_fact("Breeze(1,1)")
    kb.add_fact("Breeze(2,2)")
    kb.add_fact("Breeze(3,1)")
    # Check probability for a specific Pit location
    probability = ie.model_check_probability("Pit(2,1)")
    print(f"Probability of 'Pit(2,1)' being true with multiple Breezes: {probability}")


def test_model_check_probability_certain_pit():
    ie = init_ie()
    kb = ie.kb
    # Add Breeze facts to all four surrounding cells of (2,2)
    kb.add_fact("Breeze(1,2)")
    kb.add_fact("Breeze(3,2)")
    kb.add_fact("Breeze(2,1)")
    kb.add_fact("Breeze(2,3)")
    # Check probability for Pit(2,2)
    probability = ie.model_check_probability("Pit(2,2)")
    print(f"Probability of 'Pit(2,2)' being true with Breezes on all sides: {probability}")


def init_blank_ie(): 
    kb = KnowledgeBase()
    engine = InferenceEngine(kb, debug=True)
    return engine
def test_model_check_probability_certain_pit_case():
    ie = init_ie()
    kb = ie.kb
    # Breeze observed at (1,2) and (2,1)
    kb.add_fact("Breeze(2,2)")
    # No breeze observed at (1,1)
    kb.add_fact("!Pit(1,2)")
    kb.add_fact("!Pit(3,2)")
    kb.add_fact("!Pit(2,1)")



    # Check probability for Pit(2,2)
    probability = ie.model_check_probability("Pit(2,3)")
    print(f"Probability of 'Pit(2,3)' being true: {probability}")

def test_grounded_rules_pit_prob(): 
    bie = init_ie()
    bie.kb.add_fact("Breeze(2,2)")
    # bie.kb.add_rule("Breeze(2,2)=>Pit(2,3) | Pit(2,1) | Pit(1,2) | Pit(3,2)")
    bie.kb.add_fact("!Pit(1,2)")
    bie.kb.add_fact("!Pit(3,2)")
    bie.kb.add_fact("!Pit(2,1)") 
    res = bie.model_check_probability("Pit(2,3)") 
    print(f"Probability of 'Pit(2,3)' being true: {res}")

if __name__ == "__main__":
    test_grounded_rules_pit_prob()