from lark import Lark, Transformer
import os
import sys

# ---- Parser ----

parser = Lark(open("grammar.lark").read(), parser="lalr")


class LambdaCalculusTransformer(Transformer):
    def start(self, args):
        return args[0]
    
    def expr(self, args):
        return args[0]
    
    def add_expr(self, args):
        return args[0]
    
    def mul_expr(self, args):
        return args[0]
    
    def app_expr(self, args):
        return args[0]
    
    def atom(self, args):
        return args[0]
    
    # Note: neg_expr doesn't need a passthrough because it always has -> neg
    
    def lam(self, args):
        name, body = args
        return ("lam", str(name), body)

    def app(self, args):
        func, arg = args
        return ("app", func, arg)

    def var(self, args):
        (token,) = args
        return ("var", str(token))

    def num(self, args):
        (token,) = args
        return ("num", float(token))

    def plus(self, args):
        left, right = args
        return ("plus", left, right)

    def minus(self, args):
        left, right = args
        return ("minus", left, right)

    def times(self, args):
        left, right = args
        return ("times", left, right)

    def neg(self, args):
        (expr,) = args
        return ("neg", expr)

    def NAME(self, token):
        return str(token)

    def NUMBER(self, token):
        return str(token)


# ---- Evaluation (lazy / call-by-name) ----

def evaluate(tree):
    """Repeatedly apply a single lazy, normal-order reduction step."""
    while True:
        new_tree = reduce_once(tree)
        if new_tree == tree:
            return tree
        tree = new_tree


def reduce_once(tree):
    tag = tree[0]

    # variables and numbers are irreducible
    if tag in ("var", "num"):
        return tree

    # lazy: do NOT reduce under lambdas
    if tag == "lam":
        return tree

    # function application
    if tag == "app":
        func, arg = tree[1], tree[2]

        # normal-order: reduce function part first
        reduced_func = reduce_once(func)
        if reduced_func != func:
            return ("app", reduced_func, arg)

        # if function is a lambda, do β-reduction (call-by-name)
        if func[0] == "lam":
            _, name, body = func
            return substitute(body, name, arg)

        # lazy: don't reduce argument when function isn't a lambda
        return tree

    # arithmetic: +, -, *
    if tag in ("plus", "minus", "times"):
        left, right = tree[1], tree[2]

        # reduce left operand
        new_left = reduce_once(left)
        if new_left != left:
            return (tag, new_left, right)

        # reduce right operand
        new_right = reduce_once(right)
        if new_right != right:
            return (tag, left, new_right)

        # if both are numbers, compute
        if left[0] == "num" and right[0] == "num":
            if tag == "plus":
                return ("num", left[1] + right[1])
            elif tag == "minus":
                return ("num", left[1] - right[1])
            elif tag == "times":
                return ("num", left[1] * right[1])

        return tree

    # unary minus
    if tag == "neg":
        expr = tree[1]

        # reduce inside the negation
        new_expr = reduce_once(expr)
        if new_expr != expr:
            return ("neg", new_expr)

        # if it's a number, negate it
        if expr[0] == "num":
            return ("num", -expr[1])

        return tree

    raise Exception("Unknown tree tag in reduce_once:", tree)


# ---- Substitution (capture-avoiding) ----

class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        return "Var" + str(self.counter)


name_generator = NameGenerator()


def substitute(tree, name, replacement):
    """Capture-avoiding substitution: tree[replacement / name]."""
    tag = tree[0]

    if tag == "var":
        if tree[1] == name:
            return replacement
        else:
            return tree

    elif tag == "lam":
        bound_name = tree[1]
        body = tree[2]
        if bound_name == name:
            # shadowing
            return tree
        else:
            fresh = name_generator.generate()
            renamed_body = substitute(body, bound_name, ("var", fresh))
            return ("lam", fresh, substitute(renamed_body, name, replacement))

    elif tag == "app":
        return (
            "app",
            substitute(tree[1], name, replacement),
            substitute(tree[2], name, replacement),
        )

    elif tag == "num":
        return tree

    elif tag in ("plus", "minus", "times"):
        return (
            tag,
            substitute(tree[1], name, replacement),
            substitute(tree[2], name, replacement),
        )

    elif tag == "neg":
        return ("neg", substitute(tree[1], name, replacement))

    else:
        raise Exception("Unknown tree tag in substitute:", tree)


# ---- Pretty-printing (linearization) ----

def linearize(ast):
    tag = ast[0]

    if tag == "var":
        return ast[1]

    elif tag == "num":
        return str(ast[1])

    elif tag == "lam":
        return "(" + "\\" + ast[1] + "." + linearize(ast[2]) + ")"

    elif tag == "app":
        return "(" + linearize(ast[1]) + " " + linearize(ast[2]) + ")"

    elif tag == "plus":
        return "(" + linearize(ast[1]) + " + " + linearize(ast[2]) + ")"

    elif tag == "minus":
        return "(" + linearize(ast[1]) + " - " + linearize(ast[2]) + ")"

    elif tag == "times":
        return "(" + linearize(ast[1]) + " * " + linearize(ast[2]) + ")"

    elif tag == "neg":
        return "-" + linearize(ast[1])

    else:
        return str(ast)


# ---- Top-level interface for testing4b.py ----

def interpret(source_code: str) -> str:
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    result_ast = evaluate(ast)
    return linearize(result_ast)


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    input_arg = sys.argv[1]

    if os.path.isfile(input_arg):
        with open(input_arg, "r") as f:
            expression = f.read()
    else:
        expression = input_arg

    result = interpret(expression)
    print(result)


if __name__ == "__main__":
    main()