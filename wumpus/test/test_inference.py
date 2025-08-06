#!/usr/bin/env python3

from ..ai.knowledge_base import KnowledgeBase
from ..ai.rules_parser import Predicate
from ..ai.inference_engine import InferenceEngine

def substitution_test():
    # Test the updated inference engine
    kb = KnowledgeBase()
    kb.add_fact("Breeze(1,1)")
    kb.add_fact("Breeze(2,2)")
    kb.add_rule("Breeze(x,y) => Pit(x+1,y) | Pit(x-1,y) | Pit(x,y+1) | Pit(x,y-1)")

    ie = InferenceEngine(kb)
    print("Initial facts:", kb.get_facts())

    # Test evaluation with substitution
    test_pred = Predicate("Breeze", ["x", "y"])
    result = ie.evaluate_expression(test_pred, {"x": "1", "y": "1"})
    print(f"Evaluating Breeze(x,y) with substitution x=1, y=1: {result}")

    result2 = ie.evaluate_expression(test_pred, {"x": "3", "y": "3"})
    print(f"Evaluating Breeze(x,y) with substitution x=3, y=3: {result2}")

def forward_chaining_test():
    # Test forward chaining with the inference engine
    kb = KnowledgeBase()
    kb.add_fact("Pit(1,2)") 
    kb.add_rule("Pit(x,y) => Breeze(x+1,y) & Breeze(x-1,y) & Breeze(x,y+1) & Breeze(x,y-1)")
    
    ie = InferenceEngine(kb)
    result = ie.forward_chaining()
    print("Forward chaining results:", result)
    print("Final facts after forward chaining:", kb.get_facts())

def implies_test(): 
    kb = KnowledgeBase()
    kb.add_fact("!Breeze(1,2)") 
    kb.add_rule("!Breeze(x,y) => !Pit(x+1,y) & !Pit(x-1,y) & !Pit(x,y+1) & !Pit(x,y-1)")

    
    ie = InferenceEngine(kb) 

    parsed = kb.logic_parser.parse("!Breeze(x,y)")
    print("Parsed expression:", isinstance(parsed.expr, Predicate))
    res = ie.find_satisfying_substitutions(parsed) 
    print("Satisfying substitutions for !Pit(x,y):", res)

    parsed = kb.logic_parser.parse("!Pit(x,y)")
    res = ie.extract_facts_from_expression(parsed,{"x": "1", "y": "2"})
    print("Extracted facts from !Pit(x,y):", res)

if __name__== "__main__":
    implies_test()
    # substitution_test()
    # forward_chaining_test()
    pass 
