"""Task 3 case-study machines and representative examples."""
from .pda import make_bracket_dpda, make_marked_palindrome_dpda, make_even_palindrome_npda
from .grammars import (BRACKET_CFG, EXPRESSION_CFG, PALINDROME_CFG, LL1ExpressionParser,
                       balanced_bracket_reference, binary_palindrome_reference,
                       marked_palindrome_reference, ambiguous_expression_values,
                       parse_numeric_expression)

BRACKET_PDA = make_bracket_dpda()
MARKED_PALINDROME_PDA = make_marked_palindrome_dpda()
EVEN_PALINDROME_PDA = make_even_palindrome_npda()
EXPRESSION_PARSER = LL1ExpressionParser()

BRACKET_CASES = {
    "accepted": ["", "()", "[]{}", "([]{})", "{[()()]}", "(((())))", "()[]{}([])"],
    "rejected": ["(", ")(", "([)]", "(]", "{]", "(()", "([{}])}"],
}
EXPRESSION_CASES = {
    "accepted": ["id", "id+id*id", "(id+id)*id", "id*(id+id)", "((id))", "id+id+id"],
    "rejected": ["", "id+", "+id", "id id", "(id+id", "id*)id", "id+*id"],
}
MARKED_PALINDROME_CASES = {
    "accepted": ["#", "0#0", "001#100", "011#110", "1010#0101"],
    "rejected": ["", "01#01", "001#101", "0##0", "001100"],
}
EVEN_PALINDROME_CASES = {
    "accepted": ["", "00", "11", "0110", "1001", "001100", "10011001"],
    "rejected": ["0", "1", "010", "0101", "0010", "0111"],
}


def validate_brackets(value: str) -> bool:
    return BRACKET_PDA.simulate(value).accepted


def validate_expression(value: str) -> bool:
    return EXPRESSION_PARSER.parse(value)[0]


def validate_marked_palindrome(value: str) -> bool:
    return MARKED_PALINDROME_PDA.simulate(value).accepted


def validate_even_palindrome(value: str) -> bool:
    return EVEN_PALINDROME_PDA.simulate(value).accepted
