#!/usr/bin/env python3

from wumpus.ai.knowledge_base import KnowledgeBase
from wumpus.ai.inference_engine import InferenceEngine

# Test the updated inference engine
kb = KnowledgeBase()
kb.add_fact("Breeze(1,1)")
kb.add_fact("Breeze(2,2)")
kb.add_rule("Breeze(x,y) => Pit(x+1,y) | Pit(x-1,y) | Pit(x,y+1) | Pit(x,y-1)")

ie = InferenceEngine(kb)
print("Initial facts:", kb.get_facts())

# Test evaluation with substitution
from wumpus.ai.rules_parser import Predicate
test_pred = Predicate("Breeze", ["x", "y"])
result = ie.evaluate_expression(test_pred, {"x": "1", "y": "1"})
print(f"Evaluating Breeze(x,y) with substitution x=1, y=1: {result}")

result2 = ie.evaluate_expression(test_pred, {"x": "3", "y": "3"})
print(f"Evaluating Breeze(x,y) with substitution x=3, y=3: {result2}")
