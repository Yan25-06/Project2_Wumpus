from typing import List, Dict, Optional
from .rules_parser import LogicParser, Predicate, Not, And, Or, Implies, LogicExpr
from .knowledge_base import Fact, KnowledgeBase
import re

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

        # step 2: ground rules using known facts
        grounded_rules = []
        for rule in self.kb.rules:
            if isinstance(rule, Implies):
                for fact in self.kb.facts:
                    unify_result = self.unify(fact, rule)
                    if unify_result:
                        subs, grounded_rule = unify_result
                        grounded_rules.append(grounded_rule)
            elif isinstance(rule, Predicate):
                for fact in self.kb.facts:
                    unify_result = self.unify(fact, rule)
                    if unify_result:
                        subs, grounded_rule = unify_result
                        grounded_rules.append(grounded_rule)
            # Extend for And/Or/Not if needed

        if self.debug:
            print(f"Debug: Grounded rules from known facts: {grounded_rules}")

        # step 3 extract unknown symbols from grounded rules
        all_symbols = set()
        for gr in grounded_rules:
            if isinstance(gr, Predicate):
                all_symbols.add(gr)
            elif isinstance(gr, (And, Or, Implies, Not)):
                all_symbols.update(self.kb._flatten_logic_expr(gr))
        unknown_symbols = [s for s in all_symbols if s not in self.kb.facts]

        if self.debug:
            print(f"Debug: Unknown symbols for query '{query}': {unknown_symbols}")

        kb_true_count = 0
        query_true_count = 0

        def model_check_recursive(unknown_symbols: List[str], query: LogicExpr, model: list[Fact]) -> float:
            nonlocal kb_true_count
            nonlocal query_true_count
            if len(unknown_symbols) == 0:
                if self.is_model_satisfied(grounded_rules, model):
                    kb_true_count += 1
                    if self.is_model_satisfied([query], model):
                        query_true_count += 1
                return
            next_symbol = unknown_symbols[0]
            for truth_value in [True, False]:
                new_model = model.copy()
                if truth_value:
                    new_model.append(next_symbol)
                else:
                    if next_symbol in new_model:
                        new_model.remove(next_symbol)
                model_check_recursive(unknown_symbols[1:], query, new_model)
            return query_true_count / kb_true_count if kb_true_count > 0 else 0.5

        prob = model_check_recursive(unknown_symbols, query, self.kb.facts)
        return prob

    def _eval_math(self, expr: str, subs: Dict[str, str]) -> str:
        # basic maths, no parentheses
        """
        Evaluate simple math expressions in predicate arguments using substitutions.
        E.g., 'x+1' with subs={'x': '1'} => '2'
        """
        try:
            # Replace variables in expr with their values
            for k, v in subs.items():
                expr = expr.replace(k, v)
            # Only allow digits and math operators
            if re.match(r'^[0-9+\-*/ ]+$', expr):
                return str(eval(expr))
            return expr
        except Exception:
            return expr

    def substitute(self, expr: LogicExpr, subs: Dict[str, str]) -> LogicExpr:
        """
        Substitute variables in LogicExpr, evaluating math in predicate args.
        """
        if isinstance(expr, Predicate):
            new_args = [self._eval_math(arg, subs) for arg in expr.args]
            return Predicate(expr.name, new_args)
        elif isinstance(expr, Not):
            return Not(self.substitute(expr.expr, subs))
        elif isinstance(expr, And):
            return And(self.substitute(expr.left, subs), self.substitute(expr.right, subs))
        elif isinstance(expr, Or):
            return Or(self.substitute(expr.left, subs), self.substitute(expr.right, subs))
        elif isinstance(expr, Implies):
            return Implies(self.substitute(expr.left, subs), self.substitute(expr.right, subs))
        return expr

    def unify(self, fact: LogicExpr, rule: LogicExpr) -> Optional[Dict[str, str]]:
        """
        Unify a grounded fact (which may be any logic expression: Predicate, Not, And, Or) with the left side of a rule (which may be any logic expression).
        Returns a dict of substitutions if successful, else None.
        Handles Implies with any logic expression on the left.
        """
        def _unify_expr(fact: LogicExpr, expr: LogicExpr) -> Optional[Dict[str, str]]:
            if isinstance(fact, Predicate) and isinstance(expr, Predicate):
                if fact.name != expr.name or len(fact.args) != len(expr.args):
                    return None
                subs = {}
                for f_arg, r_arg in zip(fact.args, expr.args):
                    if r_arg.isidentifier():  # variable
                        subs[r_arg] = f_arg
                    elif r_arg != f_arg:
                        return None
                return subs
            elif isinstance(fact, Not) and isinstance(expr, Not):
                return _unify_expr(fact.expr, expr.expr)
            elif isinstance(fact, And) and isinstance(expr, And):
                left = _unify_expr(fact.left, expr.left)
                if left is not None:
                    right = _unify_expr(fact.right, expr.right)
                    if right is not None:
                        merged = left.copy()
                        merged.update(right)
                        return merged
                return None
            elif isinstance(fact, Or) and isinstance(expr, Or):
                left = _unify_expr(fact.left, expr.left)
                if left is not None:
                    right = _unify_expr(fact.right, expr.right)
                    if right is not None:
                        merged = left.copy()
                        merged.update(right)
                        return merged
                return None
            # Allow matching fact with sub-expressions of expr (for Implies, And, Or, Not)
            elif isinstance(expr, (And, Or)):
                left = _unify_expr(fact, expr.left)
                if left is not None:
                    return left
                return _unify_expr(fact, expr.right)
            elif isinstance(expr, Not):
                return _unify_expr(fact, expr.expr)
            return None

        # Unify with the left side of Implies, which can be any logic expression
        if isinstance(rule, Implies):
            subs = _unify_expr(fact, rule.left)
            if subs is not None:
                substituted_rule = self.substitute(rule, subs)
                return subs, substituted_rule
        else:
            subs = _unify_expr(fact, rule)
            if subs is not None:
                substituted_rule = self.substitute(rule, subs)
                return subs, substituted_rule
        return None

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
    kb.add_rule("Breeze(x,y) => Pit(x+1,y) | Pit(x-1,y) | Pit(x,y+1) | Pit(x,y-1)")
    engine = InferenceEngine(kb, debug=True)
    probability = engine.model_check_probability("Pit(1,2)")
    print(f"Probability of 'Pit(1,2)' being true: {probability}") # 0.5333


def test_unify():
    from .rules_parser import Predicate, Implies
    engine = InferenceEngine(None)
    parser = LogicParser()
    fact = parser.parse("fact(1,2)")

    fact2 = parser.parse("!Breeze(1,2)")
    rule = parser.parse("!Breeze(x,y) => !Pit(x+1,y) & !Pit(x-1,y) & !Pit(x,y+1) & !Pit(x,y-1)")
    result = engine.unify(fact2, rule)
    print('Unify result:', result[0] if result else None)
    print('Substituted rule:', result[1] if result else None)

def test_unify_math():
    from .rules_parser import LogicParser
    engine = InferenceEngine(None)
    parser = LogicParser()
    fact = parser.parse("fact(1,2)")
    rule = parser.parse("fact(x,y) => derived(x+1,y)")
    result = engine.unify(fact, rule)
    print('Unify result:', result[0] if result else None)
    print('Substituted rule:', result[1] if result else None)

if __name__ == "__main__": 
    # test_model_check_probability()
    # test_eval_expr()
    # test_unify()
    # test_unify_math()
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