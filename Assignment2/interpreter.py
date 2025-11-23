import sys
from lark import Lark, Transformer, Tree
import lark
import os

#  run/execute/interpret source code
def interpret(source_code):
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    result_ast = evaluate(ast)
    result = linearize(result_ast)
    return result

# convert concrete syntax to CST
parser = Lark(open("grammar.lark").read(), parser='lalr')

# convert CST to AST
class LambdaCalculusTransformer(Transformer):
    def lam(self, args):
        name, body = args
        return ('lam', str(name), body)

    def app(self, args):
        return ('app', *args)

    def var(self, args):
        token, = args
        return ('var', str(token))

    def NAME(self, token):
        return str(token)

# reduce AST to normal form (normal-order, fully normalizing)
def evaluate(tree):
    # Keep reducing until no more changes occur (normal form)
    while True:
        new_tree = reduce_once(tree)
        if new_tree == tree:
            return tree  # normal form reached
        tree = new_tree

def reduce_once(tree):
    # VAR
    if tree[0] == 'var':
        return tree

    # LAMBDA: reduce inside the body (needed for full normal form)
    if tree[0] == 'lam':
        name = tree[1]
        body = tree[2]
        reduced_body = reduce_once(body)
        if reduced_body != body:
            return ('lam', name, reduced_body)
        return tree

    # APPLICATION
    if tree[0] == 'app':
        func = tree[1]
        arg = tree[2]

        # normal order: reduce the function first
        reduced_func = reduce_once(func)
        if reduced_func != func:
            return ('app', reduced_func, arg)

        # If function is a lambda → β-reduction
        if func[0] == 'lam':
            name = func[1]
            body = func[2]
            return substitute(body, name, arg)

        # Reduce the argument only when the function cannot reduce further
        reduced_arg = reduce_once(arg)
        if reduced_arg != arg:
            return ('app', func, reduced_arg)

        # No reduction possible
        return tree

    raise Exception('Unknown tree', tree)


# generate a fresh name 
# needed eg for \y.x [y/x] --> \z.y where z is a fresh name)
class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        # user defined names start with lower case (see the grammar), thus 'Var' is fresh
        return 'Var' + str(self.counter)

name_generator = NameGenerator()

# for beta reduction (capture-avoiding substitution)
# 'replacement' for 'name' in 'tree'
def substitute(tree, name, replacement):
    # tree [replacement/name] = tree with all instances of 'name' replaced by 'replacement'
    if tree[0] == 'var':
        if tree[1] == name:
            return replacement # n [r/n] --> r
        else:
            return tree # x [r/n] --> x

    elif tree[0] == 'lam':
        if tree[1] == name:
            return tree # \n.e [r/n] --> \n.e
        else:
            fresh_name = name_generator.generate()
            return ('lam',
                    fresh_name,
                    substitute(
                        substitute(tree[2], tree[1], ('var', fresh_name)),
                        name,
                        replacement
                    ))
            # \x.e [r/n] --> (\fresh.(e[fresh/x])) [r/n]

    elif tree[0] == 'app':
        return ('app',
                substitute(tree[1], name, replacement),
                substitute(tree[2], name, replacement))

    else:
        raise Exception('Unknown tree', tree)

def linearize(ast):
    if ast[0] == 'var':
        return ast[1]
    elif ast[0] == 'lam':
        return "(" + "\\" + ast[1] + "." + linearize(ast[2]) + ")"
    elif ast[0] == 'app':
        return "(" + linearize(ast[1]) + " " + linearize(ast[2]) + ")"
    else:
        return ast

def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    input_arg = sys.argv[1]

    if os.path.isfile(input_arg):
        with open(input_arg, 'r') as file:
            expression = file.read()
    else:
        expression = input_arg

    result = interpret(expression)
    print(result)

if __name__ == "__main__":
    main()
