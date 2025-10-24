# Cpsc 354 Programming Assignment 1 — Calculator

## Collaborators 
- Savana Chou, sachou@chapman.edu
- Kaye Galang, agalang@chapman.edu
- Halle Broadnax, broadnax@chapman.edu

## Files
calculator_cfg.py
grammar.lark
specs.md

## Running Instructions
python calculator_cfg.py "expression"

Example: python  calculator_cfg.py "1+2*3"

## calculator_cfg.py

### class ASTCreator
converts the parsed tree into an AST of tuples. Each tuple contains the operation (corresponding with the grammar) and the left & right nodes

Methods:
- plus: adds left and right subexpressions
- sub: subtracts the right subexpression from the left
- mul: multiplies the left by right
- neg: multiplies the single child by -1
- log: log (left) base (right)
- exp: left raised to right
- num: integer of node

### def evaluate(ast)
recursively evaluates the value of ast representing the inputted expression. At each node, checks the current operation and performs the operation using the left & right nodes
    - plus: adds left and right subexpressions
    - sub: subtracts the right subexpression from the left
    - mul: multiplies the left by right
    - neg: multiplies the single child by -1
    - log: log (left) base (right)
    - exp: left raised to right
    - num: integer of node  

### def createParser()
loads in grammar.lark and reads the file to construct a 'lalr' parser

### def main()
- checks if user includes an expression in the arguments. If not, it exits the program
- instantiates ASTCreator
- constructs a parser
- sets the expression to the second value in the argument
- creates a tree by parsing the expression
- creates an ast of the tree using the ASTCreator
- evaluates that ast recursively

## grammar.lark
Supported operators & forms (by precedence, highest to lowest):
- Parentheses: `( … )`
- Numbers: `NUMBER` (from Lark common set)
- Unary minus: `-x`
- Exponentiation: `a ^ b` (right-associative)
- Logarithm: `log x base b`
- Multiplication: `a * b`
- Addition/Subtraction: `a + b`, `a - b`

## Program Flow
1. Validate command line to ensure there is an expression
2. instantiate ASTCreator and construct the parser
3. parse inputted expression into a tree
4. transform tree into an AST
5. recursively evaluate AST
6. print result