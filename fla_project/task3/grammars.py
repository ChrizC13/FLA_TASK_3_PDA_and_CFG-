"""Context-free grammars, derivation helpers and an LL(1) expression parser."""
from __future__ import annotations
from dataclasses import dataclass
import re
from typing import Iterable


@dataclass
class Grammar:
    start: str
    productions: dict[str, tuple[tuple[str, ...], ...]]
    terminals: set[str]

    def format(self) -> str:
        rows = []
        for lhs, alternatives in self.productions.items():
            rhs = [" ".join(option) if option else "ε" for option in alternatives]
            rows.append(f"{lhs} → " + " | ".join(rhs))
        return "\n".join(rows)


BRACKET_CFG = Grammar(
    "S",
    {"S": (("(", "S", ")", "S"), ("[", "S", "]", "S"), ("{", "S", "}", "S"), ())},
    set("()[]{}"),
)

EXPRESSION_CFG = Grammar(
    "E",
    {
        "E": (("T", "E'"),),
        "E'": (("+", "T", "E'"), ()),
        "T": (("F", "T'"),),
        "T'": (("*", "F", "T'"), ()),
        "F": (("(", "E", ")"), ("id",)),
    },
    {"+", "*", "(", ")", "id"},
)

PALINDROME_CFG = Grammar(
    "P",
    {"P": (("0", "P", "0"), ("1", "P", "1"), ("0",), ("1",), ())},
    {"0", "1"},
)

AMBIGUOUS_EXPRESSION_CFG = Grammar(
    "E",
    {"E": (("E", "+", "E"), ("E", "*", "E"), ("(", "E", ")"), ("id",))},
    {"+", "*", "(", ")", "id"},
)


@dataclass
class ParseStep:
    stack: str
    remaining_input: str
    action: str


@dataclass
class ExprNode:
    value: str
    left: "ExprNode | None" = None
    right: "ExprNode | None" = None

    def evaluate(self) -> float:
        if self.value == "+":
            return self.left.evaluate() + self.right.evaluate()  # type: ignore[union-attr]
        if self.value == "*":
            return self.left.evaluate() * self.right.evaluate()  # type: ignore[union-attr]
        return float(self.value)

    def label(self) -> str:
        return self.value


def tokenize_expression(source: str) -> list[str]:
    tokens = re.findall(r"\d+|[A-Za-z_][A-Za-z0-9_]*|[()+*]", source)
    if "".join(tokens).replace(" ", "") != re.sub(r"\s+", "", source):
        raise ValueError("Expression contains an unsupported character or token.")
    if not tokens:
        raise ValueError("Expression is empty.")
    return ["id" if token[0].isdigit() or token[0].isalpha() or token[0] == "_" else token for token in tokens]


def _token_values(source: str) -> list[str]:
    tokens = re.findall(r"\d+|[A-Za-z_][A-Za-z0-9_]*|[()+*]", source)
    if "".join(tokens).replace(" ", "") != re.sub(r"\s+", "", source):
        raise ValueError("Expression contains an unsupported character or token.")
    return tokens


class LL1ExpressionParser:
    """Predictive parser for E/T/F grammar; exposes a stack trace."""
    TABLE = {
        ("E", "id"): ("T", "E'"), ("E", "("): ("T", "E'"),
        ("E'", "+"): ("+", "T", "E'"), ("E'", ")"): (), ("E'", "$"): (),
        ("T", "id"): ("F", "T'"), ("T", "("): ("F", "T'"),
        ("T'", "*"): ("*", "F", "T'"), ("T'", "+"): (), ("T'", ")"): (), ("T'", "$"): (),
        ("F", "id"): ("id",), ("F", "("): ("(", "E", ")"),
    }
    NONTERMINALS = {"E", "E'", "T", "T'", "F"}
    TERMINALS = {"id", "+", "*", "(", ")", "$"}

    def parse(self, source: str) -> tuple[bool, list[ParseStep], str]:
        try:
            raw_tokens = _token_values(source)
        except ValueError as exc:
            return False, [ParseStep("$ E", source, f"lexical error: {exc}")], str(exc)
        tokens = ["id" if token == "id" or token[0].isdigit() or token[0].isalpha() or token[0] == "_" else token
                  for token in raw_tokens] + ["$"]
        stack = ["$", "E"]
        position = 0
        trace: list[ParseStep] = []
        while stack:
            top = stack[-1]
            lookahead = tokens[position] if position < len(tokens) else None
            before = " ".join(reversed(stack))
            remaining = " ".join(tokens[position:])
            if top == "$" and lookahead == "$":
                stack.pop()
                trace.append(ParseStep(before, remaining, "accept"))
                return True, trace, "input consumed and stack emptied"
            if top in self.TERMINALS:
                if top == lookahead:
                    stack.pop()
                    position += 1
                    trace.append(ParseStep(before, remaining, f"match {top}"))
                    continue
                trace.append(ParseStep(before, remaining, f"error: expected {top}, found {lookahead}"))
                return False, trace, f"expected {top}, found {lookahead}"
            production = self.TABLE.get((top, lookahead))
            if production is None:
                trace.append(ParseStep(before, remaining, f"error: no table entry for ({top}, {lookahead})"))
                return False, trace, f"no production for {top} with lookahead {lookahead}"
            stack.pop()
            for symbol in reversed(production):
                stack.append(symbol)
            rhs = " ".join(production) if production else "ε"
            trace.append(ParseStep(before, remaining, f"{top} -> {rhs}"))
        return False, trace, "parser stack emptied before accepting end marker"


def parse_numeric_expression(source: str) -> ExprNode:
    """Recursive-descent evaluator using the same precedence as E/T/F."""
    tokens = _token_values(source)
    position = 0

    def parse_factor() -> ExprNode:
        nonlocal position
        if position >= len(tokens):
            raise ValueError("Expected a number or parenthesised expression.")
        token = tokens[position]
        if token == "(":
            position += 1
            node = parse_expr()
            if position >= len(tokens) or tokens[position] != ")":
                raise ValueError("Missing closing parenthesis.")
            position += 1
            return node
        if token.isdigit():
            position += 1
            return ExprNode(token)
        raise ValueError(f"Numeric evaluator expected a number, found {token!r}.")

    def parse_term() -> ExprNode:
        nonlocal position
        node = parse_factor()
        while position < len(tokens) and tokens[position] == "*":
            position += 1
            node = ExprNode("*", node, parse_factor())
        return node

    def parse_expr() -> ExprNode:
        nonlocal position
        node = parse_term()
        while position < len(tokens) and tokens[position] == "+":
            position += 1
            node = ExprNode("+", node, parse_term())
        return node

    result = parse_expr()
    if position != len(tokens):
        raise ValueError(f"Unexpected token {tokens[position]!r}.")
    return result


def ambiguous_expression_values(a: int = 2, b: int = 3, c: int = 4) -> tuple[int, int]:
    """Two groupings licensed by E -> E+E | E*E | (E) | id."""
    return a + (b * c), (a + b) * c


def balanced_bracket_reference(source: str) -> bool:
    stack: list[str] = []
    matching = {")": "(", "]": "[", "}": "{"}
    for character in source:
        if character in "([{":
            stack.append(character)
        elif character in ")]}":
            if not stack or stack.pop() != matching[character]:
                return False
        else:
            return False
    return not stack


def binary_palindrome_reference(source: str) -> bool:
    return all(character in "01" for character in source) and source == source[::-1]


def marked_palindrome_reference(source: str) -> bool:
    if source.count("#") != 1:
        return False
    left, right = source.split("#")
    return all(character in "01" for character in left + right) and left == right[::-1]
