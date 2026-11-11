from itertools import product

from fla_project.task3.cases import (BRACKET_CASES, EXPRESSION_CASES, MARKED_PALINDROME_CASES,
    EVEN_PALINDROME_CASES, BRACKET_PDA, MARKED_PALINDROME_PDA, EVEN_PALINDROME_PDA,
    validate_brackets, validate_expression, validate_marked_palindrome, validate_even_palindrome)
from fla_project.task3.grammars import (balanced_bracket_reference, binary_palindrome_reference,
    marked_palindrome_reference, ambiguous_expression_values, parse_numeric_expression,
    LL1ExpressionParser)


def test_bracket_case_examples():
    assert all(validate_brackets(x) for x in BRACKET_CASES["accepted"])
    assert not any(validate_brackets(x) for x in BRACKET_CASES["rejected"])
    assert BRACKET_PDA.is_deterministic()


def test_brackets_exhaustive_short_strings():
    alphabet = "()[]{}x"
    for length in range(5):
        for chars in product(alphabet, repeat=length):
            value = "".join(chars)
            assert validate_brackets(value) == balanced_bracket_reference(value)


def test_expression_valid_invalid_and_precedence():
    assert all(validate_expression(x) for x in EXPRESSION_CASES["accepted"])
    assert not any(validate_expression(x) for x in EXPRESSION_CASES["rejected"])
    assert parse_numeric_expression("2+3*4").evaluate() == 14
    assert parse_numeric_expression("(2+3)*4").evaluate() == 20
    assert ambiguous_expression_values() == (14, 20)


def test_expression_parser_rejects_bad_tokens():
    parser = LL1ExpressionParser()
    for bad in ["", "id+", "(id", "id**id", "id id", "id/@id"]:
        assert parser.parse(bad)[0] is False


def test_marked_palindrome_examples_and_determinism():
    assert all(validate_marked_palindrome(x) for x in MARKED_PALINDROME_CASES["accepted"])
    assert not any(validate_marked_palindrome(x) for x in MARKED_PALINDROME_CASES["rejected"])
    assert MARKED_PALINDROME_PDA.is_deterministic()


def test_even_palindrome_npda_examples():
    assert all(validate_even_palindrome(x) for x in EVEN_PALINDROME_CASES["accepted"])
    assert not any(validate_even_palindrome(x) for x in EVEN_PALINDROME_CASES["rejected"])
    assert not EVEN_PALINDROME_PDA.is_deterministic()


def test_palindrome_reference_agreement_short_strings():
    for length in range(7):
        for chars in product("01", repeat=length):
            value = "".join(chars)
            # The NPDA models even-length palindromes only.
            reference_even = binary_palindrome_reference(value) and len(value) % 2 == 0
            assert validate_even_palindrome(value) == reference_even
            marked = value + "#" + value[::-1]
            assert validate_marked_palindrome(marked) == marked_palindrome_reference(marked)
