# grammar.py
"""
This file contains the Lark grammar for the calculator.
It defines operator precedence and associativity explicitly.
"""

GRAMMAR = r"""
?start: exp

?exp: sum

?sum: sum "+" term   -> add
    | sum "-" term   -> sub
    | term

?term: term "*" unary -> mul
     | unary

?unary: "-" unary     -> neg
      | pow

?pow: primary "^" pow -> pow
    | primary

?primary: "log" exp "base" exp -> log
        | NUMBER                     -> number
        | "(" exp ")"

%import common.NUMBER
%import common.WS_INLINE
%ignore WS_INLINE
"""
