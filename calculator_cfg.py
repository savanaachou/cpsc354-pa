"""
calculator_cfg.py

Usage:
    python calculator_cfg.py "1+2*3"

This script builds an AST using Lark and then evaluates it recursively.
"""
import sys
import math
from lark import Lark, Transformer
from grammar import GRAMMAR  # import the grammar string

# Build parser from grammar string
parser = Lark(GRAMMAR, start='start', parser='lalr')