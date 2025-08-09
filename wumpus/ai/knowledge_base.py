from .rules_parser import LogicExpr, LogicParser, Predicate, Not, And, Or, Implies 
from typing import Union


Fact = LogicExpr

class KnowledgeBase:
    def __init__(self):
        self.facts: list[Fact] = []
        self.rules: list[LogicExpr] = []
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

    def get_rules(self): 
        return self.rules


    def get_flatten_rules_symbols(self) -> list[Fact]:
        """Get all unique symbols from the rules in the knowledge base."""
        symbols = set()
        for rule in self.rules:
            if isinstance(rule, Predicate):
                symbols.add(rule)
            elif isinstance(rule, (And, Or, Implies, Not)):
                symbols.update(self._flatten_logic_expr(rule))
        return list(symbols)

    def _flatten_logic_expr(self, expr: LogicExpr) -> set[Fact]:
        """Recursively flatten logic expressions to extract symbols."""
        if isinstance(expr, Predicate):
            return {expr}
        elif isinstance(expr, Not):
            return self._flatten_logic_expr(expr.expr)
        elif isinstance(expr, (And, Or, Implies)):
            return self._flatten_logic_expr(expr.left) | self._flatten_logic_expr(expr.right)
        return set()


    def update_kb(self, percepts): 
        pass 

