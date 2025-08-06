from typing import List, Dict, Optional
from .rules_parser import LogicParser, Predicate, Not, And, Or, Implies, LogicExpr
from .knowledge_base import Fact, KnowledgeBase
import random

class InferenceEngine:
    def __init__(self, kb: KnowledgeBase, debug: bool = False):
        self.kb = kb
        self.debug = debug
    

    def get_unknown_symbols(self) -> List[Fact]:

        all_symbols = self.kb.get_flatten_rules_symbols()
        unknown_symbols = [s for s in all_symbols if s not in self.kb.facts]
        return unknown_symbols
    
    def evaluate_expr(self, expression: LogicExpr, model: List[Fact]) -> bool:
        """
        Evaluate a single logic expression against a model.
        Returns True if the expression is satisfied by the model.
        """
        if self.debug:
            print(f"Debug: Evaluating expression {expression} against model {model}")
        if isinstance(expression, Predicate):
            return expression in model
        elif isinstance(expression, Not):
            return not self.evaluate_expr(expression.expr, model)
        elif isinstance(expression, And):
            return self.evaluate_expr(expression.left, model) and self.evaluate_expr(expression.right, model)
        elif isinstance(expression, Or):
            return self.evaluate_expr(expression.left, model) or self.evaluate_expr(expression.right, model)
        elif isinstance(expression, Implies):
            return not self.evaluate_expr(expression.left, model) or self.evaluate_expr(expression.right, model)

        if self.debug:
            print(f"Debug: Unknown expression type {type(expression)}")
        return False

    def is_model_satisfied(self, expressions: List[LogicExpr], model: List[Fact]) -> bool:
        """
        Evaluate a list of logic expressions against a model.
        Returns True if all expressions are satisfied by the model.
        """
        for expr in expressions:
            if not self.evaluate_expr(expr, model):
                if self.debug:
                    print(f"Debug: Expression {expr} is not satisfied by model {model}")
                return False
        return True

    def model_check_probability(self, query: LogicExpr | str) -> float:  
        if isinstance(query, str): 
            query = LogicParser().parse(query) 

        # step 1 direct fact checking 
        if isinstance(query, Predicate) and query in self.kb.facts:
            return 1.0

        # step 2 extract unknown symbols 
        unknown_symbols = self.get_unknown_symbols()

        if self.debug:
            print(f"Debug: Unknown symbols for query '{query}': {unknown_symbols}")

        # step 3 recursively handle unknown symbols, trying all combinations of truth values

        kb_true_count = 0
        query_true_count = 0

        def model_check_recursive(unknown_symbols: List[str], query: LogicExpr, model: list[Fact]) -> float: 
            nonlocal kb_true_count 
            nonlocal query_true_count 

            # base case: no unkown symbols left 
            if len(unknown_symbols) == 0:
                if self.is_model_satisfied(self.kb.rules,model): 
                    if self.debug:
                        print(f"Debug: Found satisfied model {model} for KB")
                    kb_true_count += 1
                    if self.is_model_satisfied([query], model): 
                        if self.debug:
                            print(f"Debug: Found satisfied model {model} for query {query}")
                        query_true_count += 1
                return

            # generate next symbol with different truth values to try
            next_symbol = unknown_symbols[0] 
            for truth_value in [True, False]:
                new_model = model.copy()
                if truth_value:
                    new_model.append(next_symbol)
                # false = absence of the symbol
                else:
                    if next_symbol in new_model:
                        new_model.remove(next_symbol)   

                # recursively check the rest of the unknown symbols
                model_check_recursive(unknown_symbols[1:], query, new_model)
            
            if self.debug:
                if kb_true_count == 0: 
                    print(f"Debug: No valid models found for {unknown_symbols} with query {query}")
                else: 
                    print(f"Debug: Found {query_true_count} valid query models, with {kb_true_count} kb valid models for {unknown_symbols} with query {query}")


            return query_true_count / kb_true_count if kb_true_count > 0 else 0.5

        if self.debug:
            print(f"Debug: Starting model checking for query '{query}' with unknown symbols {unknown_symbols} and facts {self.kb.facts}")
        prob = model_check_recursive(unknown_symbols, query, self.kb.facts)


        return prob







def test_eval_expr():
    kb = KnowledgeBase()
    kb.add_fact("Breeze(1,1)")
    kb.add_fact("Pit(2,1)")
    kb.add_rule("Breeze(1,1) => Pit(2,1) | Pit(0,1) | Pit(1,2) | Pit(1,0)")
    
    engine = InferenceEngine(kb, debug=True)

    res = engine.is_model_satisfied(kb.rules, kb.facts) 
    print(f"Evaluation result: {res}")  # Should print True if Breeze(1,1) is a fact

def test_get_unknown():
    kb = KnowledgeBase()
    kb.add_fact("Breeze(1,1)")
    # kb.add_rule("Breeze(x,y) => Pit(x+1,y) | Pit(x-1,y) | Pit(x,y+1) | Pit(x,y-1)")
    kb.add_rule("Breeze(1,1) => Pit(2,1) | Pit(0,1) | Pit(1,2) | Pit(1,0)")
    
    engine = InferenceEngine(kb)

    unknown_symbols = engine.get_unknown_symbols()
    print(f"Unknown symbols for query 'Pit(1,2)': {unknown_symbols}")

def test_model_check_probability():
    kb = KnowledgeBase()
    kb.add_fact("Breeze(1,1)")
    kb.add_rule("Breeze(1,1) => Pit(2,1) | Pit(0,1) | Pit(1,2) | Pit(1,0)")
    engine = InferenceEngine(kb, debug=True)
    probability = engine.model_check_probability("Pit(1,2)")
    print(f"Probability of 'Pit(1,2)' being true: {probability}") # 0.5333


if __name__ == "__main__": 
    test_model_check_probability()
    # test_eval_expr()
    pass

def main():
    kb = KnowledgeBase()
    kb.add_rule("Breeze(x,y) => Pit(x+1,y) | Pit(x-1,y) | Pit(x,y+1) | Pit(x,y-1)")
    kb.add_fact("Breeze(1,1)")
    
    engine = InferenceEngine(kb, debug=True)
    
    # parsed_query = LogicParser().parse("Pit(1,2)")
    # result = engine.model_checking_probability(parsed_query)
    
    # print(f"Final probability: {result}")

    parser = LogicParser()
    kb_expr = parser.parse("Breeze(x,y) => Pit(x+1,y) | Pit(x-1,y) | Pit(x,y+1) | Pit(x,y-1)")
    query = parser.parse("Pit(1,2)")
    symbols = ["Pit(1,2)"]  
    model = {"Breeze(1,1)": True}  # Known facts
    probability = engine.model_pos(symbols, model, kb_expr, query)
    print(f"Probability of query being true: {probability}")