from lark import Lark, Transformer
import os
import sys

parser = Lark(open("grammar.lark").read(), parser="lalr", lexer="contextual")


class LambdaCalculusTransformer(Transformer):
    def start(self, args):
        return args[0]

    def seq_expr(self, args):
        if len(args) == 1:
            return args[0]
        return args[0]  # Grammar handles this

    def lam_expr(self, args):
        return args[0]

    def if_expr(self, args):
        return args[0]

    def letrec_expr(self, args):
        return args[0]

    def let_expr(self, args):
        return args[0]

    def fix_expr(self, args):
        return args[0]

    def eq_expr(self, args):
        return args[0]

    def leq_expr(self, args):
        return args[0]

    def cons_expr(self, args):
        return args[0]

    def hd_tl_expr(self, args):
        return args[0]

    def add_expr(self, args):
        return args[0]

    def mul_expr(self, args):
        return args[0]

    def app_expr(self, args):
        return args[0]

    def neg_atom(self, args):
        return args[0]

    def atom(self, args):
        return args[0]

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

    def ifexp(self, args):
        c, t, e = args
        return ("if", c, t, e)

    def letexp(self, args):
        name, value, body = args
        return ("let", str(name), value, body)

    def letrecexp(self, args):
        name, value, body = args
        return ("letrec", str(name), value, body)

    def eq(self, args):
        a, b = args
        return ("eq", a, b)

    def leq(self, args):
        a, b = args
        return ("leq", a, b)

    def nil(self, _args):
        return ("nil",)

    def cons(self, args):
        h, t = args
        return ("cons", h, t)

    def hd(self, args):
        (xs,) = args
        return ("hd", xs)

    def tl(self, args):
        (xs,) = args
        return ("tl", xs)

    def prog(self, args):
        left, right = args
        return ("prog", left, right)

    def fix(self, args):
        (expr,) = args
        return ("fix", expr)

    def NAME(self, token):
        return str(token)

    def NUMBER(self, token):
        return str(token)


def evaluate(tree):
    while True:
        new_tree = reduce_once(tree)
        if new_tree == tree:
            return tree
        tree = new_tree


def reduce_once(tree):
    tag = tree[0]

    if tag in ("var", "num", "nil"):
        return tree

    if tag == "lam":
        return tree

    if tag == "cons":
        h, t = tree[1], tree[2]
        new_h = reduce_once(h)
        if new_h != h:
            return ("cons", new_h, t)
        new_t = reduce_once(t)
        if new_t != t:
            return ("cons", h, new_t)
        return tree

    if tag == "prog":
        # Evaluate left side first
        left, right = tree[1], tree[2]
        new_left = reduce_once(left)
        if new_left != left:
            return ("prog", new_left, right)
        # Once left is fully evaluated, evaluate right
        new_right = reduce_once(right)
        if new_right != right:
            return ("prog", left, new_right)
        return tree

    if tag == "app":
        func, arg = tree[1], tree[2]
        reduced_func = reduce_once(func)
        if reduced_func != func:
            return ("app", reduced_func, arg)
        if func[0] == "lam":
            _, name, body = func
            return substitute(body, name, arg)
        return tree

    if tag in ("plus", "minus", "times"):
        left, right = tree[1], tree[2]
        new_left = reduce_once(left)
        if new_left != left:
            return (tag, new_left, right)
        new_right = reduce_once(right)
        if new_right != right:
            return (tag, left, new_right)
        if left[0] == "num" and right[0] == "num":
            if tag == "plus":
                return ("num", left[1] + right[1])
            if tag == "minus":
                return ("num", left[1] - right[1])
            if tag == "times":
                return ("num", left[1] * right[1])
        return tree

    if tag == "neg":
        expr = tree[1]
        new_expr = reduce_once(expr)
        if new_expr != expr:
            return ("neg", new_expr)
        if expr[0] == "num":
            return ("num", -expr[1])
        return tree

    if tag == "if":
        cond, thn, els = tree[1], tree[2], tree[3]
        new_cond = reduce_once(cond)
        if new_cond != cond:
            return ("if", new_cond, thn, els)
        if cond[0] == "num":
            return thn if cond[1] != 0 else els
        return tree

    if tag == "let":
        name, value, body = tree[1], tree[2], tree[3]
        return ("app", ("lam", name, body), value)

    if tag == "letrec":
        name, value, body = tree[1], tree[2], tree[3]
        Y = (
            "lam",
            "f",
            (
                "app",
                ("lam", "x", ("app", ("var", "f"), ("app", ("var", "x"), ("var", "x")))),
                ("lam", "x", ("app", ("var", "f"), ("app", ("var", "x"), ("var", "x")))),
            ),
        )
        fix_value = ("app", Y, ("lam", name, value))
        return ("app", ("lam", name, body), fix_value)

    if tag == "fix":
        # fix F --> F (fix F)
        f = tree[1]
        return ("app", f, tree)

    if tag == "hd":
        xs = tree[1]
        new_xs = reduce_once(xs)
        if new_xs != xs:
            return ("hd", new_xs)
        if xs[0] == "cons":
            return xs[1]
        return tree

    if tag == "tl":
        xs = tree[1]
        new_xs = reduce_once(xs)
        if new_xs != xs:
            return ("tl", new_xs)
        if xs[0] == "cons":
            return xs[2]
        return tree

    if tag == "eq":
        a, b = tree[1], tree[2]
        new_a = reduce_once(a)
        if new_a != a:
            return ("eq", new_a, b)
        new_b = reduce_once(b)
        if new_b != b:
            return ("eq", a, new_b)

        def force(x):
            if x[0] != "cons":
                return x
            h, t = x[1], x[2]
            nh = reduce_once(h)
            if nh != h:
                return ("cons", nh, t)
            nt = reduce_once(t)
            if nt != t:
                return ("cons", h, nt)
            return x

        fa = force(a)
        if fa != a:
            return ("eq", fa, b)
        fb = force(b)
        if fb != b:
            return ("eq", a, fb)

        def eqv(x, y):
            if x[0] == "num" and y[0] == "num":
                return x[1] == y[1]
            if x[0] == "nil" and y[0] == "nil":
                return True
            if x[0] == "cons" and y[0] == "cons":
                return eqv(x[1], y[1]) and eqv(x[2], y[2])
            return False

        if a[0] in ("num", "nil", "cons") and b[0] in ("num", "nil", "cons"):
            return ("num", 1.0 if eqv(a, b) else 0.0)
        return tree

    if tag == "leq":
        a, b = tree[1], tree[2]
        new_a = reduce_once(a)
        if new_a != a:
            return ("leq", new_a, b)
        new_b = reduce_once(b)
        if new_b != b:
            return ("leq", a, new_b)
        if a[0] == "num" and b[0] == "num":
            return ("num", 1.0 if a[1] <= b[1] else 0.0)
        return tree

    raise Exception("Unknown tree tag in reduce_once:", tree)


class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        return "Var" + str(self.counter)


name_generator = NameGenerator()


def substitute(tree, name, replacement):
    tag = tree[0]

    if tag == "var":
        return replacement if tree[1] == name else tree

    if tag == "lam":
        bound, body = tree[1], tree[2]
        if bound == name:
            return tree
        fresh = name_generator.generate()
        renamed = substitute(body, bound, ("var", fresh))
        return ("lam", fresh, substitute(renamed, name, replacement))

    if tag == "app":
        return ("app", substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))

    if tag == "num":
        return tree

    if tag in ("plus", "minus", "times"):
        return (tag, substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))

    if tag == "neg":
        return ("neg", substitute(tree[1], name, replacement))

    if tag == "if":
        return ("if",
                substitute(tree[1], name, replacement),
                substitute(tree[2], name, replacement),
                substitute(tree[3], name, replacement))

    if tag == "let":
        x, v, body = tree[1], tree[2], tree[3]
        nv = substitute(v, name, replacement)
        if x == name:
            return ("let", x, nv, body)
        return ("let", x, nv, substitute(body, name, replacement))

    if tag == "letrec":
        f, v, body = tree[1], tree[2], tree[3]
        if f == name:
            return tree
        return ("letrec", f, substitute(v, name, replacement), substitute(body, name, replacement))

    if tag == "eq":
        return ("eq", substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))

    if tag == "leq":
        return ("leq", substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))

    if tag == "nil":
        return tree

    if tag == "cons":
        return ("cons", substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))

    if tag == "hd":
        return ("hd", substitute(tree[1], name, replacement))

    if tag == "tl":
        return ("tl", substitute(tree[1], name, replacement))

    if tag == "prog":
        return ("prog", substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))

    if tag == "fix":
        return ("fix", substitute(tree[1], name, replacement))

    raise Exception("Unknown tree tag in substitute:", tree)


def linearize(ast):
    tag = ast[0]

    if tag == "var":
        return ast[1]

    if tag == "num":
        return str(ast[1])

    if tag == "lam":
        return "(\\" + ast[1] + "." + linearize(ast[2]) + ")"

    if tag == "app":
        return "(" + linearize(ast[1]) + " " + linearize(ast[2]) + ")"

    if tag == "plus":
        return "(" + linearize(ast[1]) + " + " + linearize(ast[2]) + ")"

    if tag == "minus":
        return "(" + linearize(ast[1]) + " - " + linearize(ast[2]) + ")"

    if tag == "times":
        return "(" + linearize(ast[1]) + " * " + linearize(ast[2]) + ")"

    if tag == "neg":
        return "-" + linearize(ast[1])

    if tag == "if":
        return "(if " + linearize(ast[1]) + " then " + linearize(ast[2]) + " else " + linearize(ast[3]) + ")"

    if tag == "let":
        return "(let " + ast[1] + " = " + linearize(ast[2]) + " in " + linearize(ast[3]) + ")"

    if tag == "letrec":
        return "(letrec " + ast[1] + " = " + linearize(ast[2]) + " in " + linearize(ast[3]) + ")"

    if tag == "eq":
        return "(" + linearize(ast[1]) + " == " + linearize(ast[2]) + ")"

    if tag == "leq":
        return "(" + linearize(ast[1]) + " <= " + linearize(ast[2]) + ")"

    if tag == "nil":
        return "#"

    if tag == "cons":
        return "(" + linearize(ast[1]) + " : " + linearize(ast[2]) + ")"

    if tag == "hd":
        return "(hd " + linearize(ast[1]) + ")"

    if tag == "tl":
        return "(tl " + linearize(ast[1]) + ")"

    if tag == "prog":
        return linearize(ast[1]) + " ;; " + linearize(ast[2])

    if tag == "fix":
        return "(fix " + linearize(ast[1]) + ")"

    return str(ast)


def interpret(source_code: str) -> str:
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    result_ast = evaluate(ast)
    return linearize(result_ast)


def main():
    if len(sys.argv) != 2:
        sys.exit(1)
    arg = sys.argv[1]
    if os.path.isfile(arg):
        with open(arg) as f:
            expr = f.read()
    else:
        expr = arg
    print(interpret(expr))


if __name__ == "__main__":
    main()