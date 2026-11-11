from __future__ import annotations
import argparse
from .cases import (BRACKET_CASES, EXPRESSION_CASES, MARKED_PALINDROME_CASES, EVEN_PALINDROME_CASES,
                    BRACKET_PDA, MARKED_PALINDROME_PDA, EVEN_PALINDROME_PDA,
                    EXPRESSION_PARSER, validate_brackets, validate_expression,
                    validate_marked_palindrome, validate_even_palindrome)
from .grammars import (BRACKET_CFG, EXPRESSION_CFG, PALINDROME_CFG, ambiguous_expression_values,
                       parse_numeric_expression)


def run_all() -> None:
    print("TASK 3 - PDA AND CFG CASE STUDIES")
    print("\n1. Balanced delimiters")
    print(BRACKET_CFG.format())
    for label, values in BRACKET_CASES.items():
        print(f"  {label.title()}")
        for value in values:
            print(f"    {'ACCEPT' if validate_brackets(value) else 'REJECT':6} {value!r}")
    trace = BRACKET_PDA.simulate("{[()]}")
    print("  Sample stack trace for '{[()]}'")
    for state, pos, stack, action in trace.path:
        print(f"    state={state:<5} input-position={pos:<2} stack={''.join(stack)!r:<12} action={action}")

    print("\n2. Arithmetic expressions")
    print(EXPRESSION_CFG.format())
    for label, values in EXPRESSION_CASES.items():
        print(f"  {label.title()}")
        for value in values:
            print(f"    {'ACCEPT' if validate_expression(value) else 'REJECT':6} {value!r}")
    ambiguous = ambiguous_expression_values()
    parsed = parse_numeric_expression("2+3*4")
    print(f"  Precedence-aware evaluation: 2+3*4 = {parsed.evaluate():g}")
    print(f"  Ambiguous grammar alternatives: {ambiguous[0]} versus {ambiguous[1]}")
    accepted, parse_trace, reason = EXPRESSION_PARSER.parse("id+id*id")
    print(f"  Predictive PDA trace (accepted={accepted}):")
    for step in parse_trace:
        print(f"    stack=[{step.stack}] input=[{step.remaining_input}] action={step.action}")

    print("\n3. Binary palindromes")
    print(PALINDROME_CFG.format())
    for label, values in MARKED_PALINDROME_CASES.items():
        print(f"  Marked form {label}")
        for value in values:
            print(f"    {'ACCEPT' if validate_marked_palindrome(value) else 'REJECT':6} {value!r}")
    for label, values in EVEN_PALINDROME_CASES.items():
        print(f"  Unmarked even form {label}")
        for value in values:
            print(f"    {'ACCEPT' if validate_even_palindrome(value) else 'REJECT':6} {value!r}")
    print("  Determinism:")
    print("   Bracket DPDA:", BRACKET_PDA.is_deterministic())
    print("   Marked-palindrome DPDA:", MARKED_PALINDROME_PDA.is_deterministic())
    print("   Unmarked-even-palindrome NPDA:", EVEN_PALINDROME_PDA.is_deterministic())


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Task 3 - PDA and CFG case studies")
    parser.add_argument("case", nargs="?", choices=["all", "brackets", "expr", "palindrome"], default="all")
    parser.add_argument("value", nargs="?", help="Optional input to validate")
    args = parser.parse_args(argv)
    if args.value is None:
        run_all()
        return
    if args.case == "brackets":
        result = BRACKET_PDA.simulate(args.value)
        print("ACCEPT" if result.accepted else "REJECT", "|", result.reason)
        for row in result.path:
            print(row)
    elif args.case == "expr":
        accepted, trace, reason = EXPRESSION_PARSER.parse(args.value)
        print("ACCEPT" if accepted else "REJECT", "|", reason)
        for step in trace:
            print(step)
    elif args.case == "palindrome":
        marked = "#" in args.value
        pda = MARKED_PALINDROME_PDA if marked else EVEN_PALINDROME_PDA
        result = pda.simulate(args.value)
        print("ACCEPT" if result.accepted else "REJECT", "|", result.reason)
        for row in result.path:
            print(row)
    else:
        parser.error("Choose brackets, expr, or palindrome when supplying an input.")


if __name__ == "__main__":
    main()
