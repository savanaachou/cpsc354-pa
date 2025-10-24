"""
calculator_cfg.py

Usage:
    python calculator_cfg.py "1+2*3"

This script builds an AST using Lark and then evaluates it recursively.
"""
import sys
import math
from lark import Lark, Transformer

class ASTCreator(Transformer):
    def plus(self, items):
        return('plus', items[0], items[1])
    def sub(self, items):
        return('sub', items[0], items[1])
    def mul(self, items):
        return('mul', items[0], items[1])
    def neg(self, items):
        return('neg', items[0])
    def log(self, items):
        return('log', items[0], items[1])
    def exp(self, items):
        return('exp', items[0], items[1])
    def num(self, items):
        return('num', int(items[0]))
    
def evaluate(ast):
    if ast[0] == 'plus':
        return evaluate(ast[1]) + evaluate(ast[2])
    elif ast[0] == 'sub':
        return evaluate(ast[1]) - evaluate(ast[2])
    elif ast[0] == 'mul':
        return evaluate(ast[1]) * evaluate(ast[2])
    elif ast[0] == 'neg':
        return evaluate(ast[1]) * -1
    elif ast[0] == 'log':
        return math.log(evaluate(ast[1]), evaluate(ast[2]))
    elif ast[0] == 'exp':
        return evaluate(ast[1]) ** evaluate(ast[2])
    elif ast[0] == 'num':
        return ast[1]
    else:
        raise ValueError(f"Unknown operation: {ast}")
    
def createParser():
    with open("grammar.lark", "r") as grammar_file:
        grammar = grammar_file.read()

    return Lark(grammar, parser='lalr')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python calculator_cfg.py <expression>")
        sys.exit(1)

    ast_creator = ASTCreator()
    parser = createParser()
    expression = sys.argv[1]
    tree = parser.parse(expression)
    ast = ast_creator.transform(tree)
    result = evaluate(ast)
    print(result)

    