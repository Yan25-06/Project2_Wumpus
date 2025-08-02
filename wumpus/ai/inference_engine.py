from dataclasses import dataclass
from enum import Enum

from ..ai.rules_parser import LogicExpr, LogicParser, Predicate, Not, And, Or, Implies
from ..agents.agent import Agent

class InferenceEngine(): 
    pass 



facts = ["Breeze(1,1)", "Stench(1,2)"]
knowledge_base = []
rules = []


class KnowledgeBase:
    def __init__(self):
        self.facts: list[Predicate] = []
        self.rules: list[Predicate] = []
        self.logic_parser = LogicParser()


    def add_fact(self, fact_str: str):
        print(f"Adding fact: {fact_str}")
        fact = self.logic_parser.parse(fact_str)
        self.facts.append(fact)

    def add_rule(self, rule_str: str):
        print(f"Adding rule: {rule_str}")
        rule = self.logic_parser.parse(rule_str)
        self.rules.append(rule)

    def get_facts(self):
        return self.facts


    def match_predicate_with_variables(self, fact: Predicate, predicate: Predicate):
        fact_name, fact_args = fact.__class__.__name__, fact.args
        if fact_name != predicate.__class__.__name__:
            return False
        if len(fact_args) != len(predicate.args):
            return False

        # Check if all arguments match or can be substituted
        substitutions = {}
        for fact_arg, pred_arg in zip(fact_args, predicate.args):
            if pred_arg.isidentifier():
                if pred_arg not in substitutions:
                    substitutions[pred_arg] = fact_arg
                elif substitutions[pred_arg] != fact_arg:
                    return False
            elif fact_arg != pred_arg:
                return False
            
        # If we reach here, the predicate matches with the substitutions
        return True


    def evaluate_expression(self, expr):
        """Check if an entire antecedent expression is satisfied"""
        if isinstance(expr, Predicate):
            return any(self.match_predicate_with_variables(fact, expr) for fact in self.facts)
        elif isinstance(expr, And):
            return (self.evaluate_expression(expr.left) and 
                    self.evaluate_expression(expr.right))
        elif isinstance(expr, Or):
            return (self.evaluate_expression(expr.left) or 
                    self.evaluate_expression(expr.right))
        elif isinstance(expr, Not):
            return not self.evaluate_expression(expr.expr)
        return False

    def forward_chaining(self, start_fact: str): 
        """Perform FC until no new facts can be inferred."""
        new_facts = True
        while new_facts:
            new_facts = False
            for rule in self.rules: 
                if not isinstance(rule, Implies):
                    raise ValueError("Rule must be an implication (=>)")

                lhs, rhs = rule.left, rule.right
                # If lhs (condition) is satisfied
                if self.evaluate_expression(lhs):
                    # Add rhs if not already known
                    if rhs not in self.facts:
                        self.add_fact(rhs.__str__())
                        new_facts = True
        return self.facts

# TODO: split KnowledgeBase and InferenceEngine

if __name__ == "__main__":
    kb = KnowledgeBase()
    kb.add_fact("Breeze(1,1)")
    kb.add_rule("Breeze(x,y) => Pit(x+1,y) | Pit(x-1,y) | Pit(x,y+1) | Pit(x,y-1)")

    print("Initial Facts:", kb.get_facts())
    res = kb.forward_chaining("Breeze(1,1)")
    print("Inferred Facts:", res)