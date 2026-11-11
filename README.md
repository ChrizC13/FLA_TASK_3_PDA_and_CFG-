# Task 3 - Pushdown Automata and Context-Free Grammar Case Studies

**Student:** Chris Jero Harsha P  
**Register No.:** RA2411026050010  
**Course:** 21CSC301T - Formal Language and Automata  
**Institution:** SRM Institute of Science and Technology, Tiruchirappalli

This package models three context-free case studies:

1. **Balanced delimiters:** a deterministic PDA pushes opening delimiters and pops only matching closing delimiters. A CFG describes recursively nested balanced blocks.
2. **Arithmetic expressions:** an ambiguous grammar is contrasted with a precedence grammar. A predictive stack parser enforces multiplication precedence over addition.
3. **Binary palindromes:** a DPDA recognises the marked form `w#reverse(w)`. An NPDA recognises even-length unmarked palindromes by nondeterministically guessing the midpoint. A CFG generates binary palindromes.

## Quick start

Python 3.10+ is recommended. The automata/PDA implementation uses the Python standard library.

```bash
# Run all Task 3 demonstrations
python -m fla_project

# Validate a specific input and print stack/parser traces
python -m fla_project brackets '([]{})'
python -m fla_project expr 'id+id*id'
python -m fla_project palindrome '001#100'
python -m fla_project palindrome '0110'

# Run Task 3 tests
python -m pytest -q
```

Install the development dependency before running tests:

```bash
python -m pip install -r requirements-dev.txt
```

## Browser demonstration

Open `docs/index.html` directly in a browser. The page is a local static demonstration and does not send input to a server.

## Diagrams and visualisations

The `docs/diagrams/` folder contains PNG, SVG and Graphviz DOT figures for the models in this task. To regenerate PNG/SVG files, install Graphviz and run:

```bash
python tools/render_diagrams.py
```

The browser demo and command-line output samples are included under `docs/`.

## Test coverage

The Task 3 tests cover accepted/rejected delimiter examples, exhaustive short delimiter strings against an independent stack checker, arithmetic precedence and malformed expressions, marked and unmarked palindrome cases, bounded palindrome cross-checks, and PDA determinism properties.


## Modelling limitations

- The bracket PDA models delimiters after tokenisation; a full language lexer/parser requires additional lexical and grammar rules.
- The expression parser supports identifiers or integers, parentheses, addition, and multiplication; it is not a complete programming-language parser.
- The NPDA simulation explores nondeterministic configurations up to a configured cap.


## Report

A task-specific PDF extract is provided in `report/`. It contains a dedicated task cover, the corresponding task section from the consolidated report, and its references. The original page numbering within the extracted section is retained.

## Academic integrity note

This repository is an AI-assisted working draft. Review and understand the implementation, rerun the tests, adapt the work to your own understanding, and follow your course's AI-acknowledgement and independent-work requirements before submission.

## Reference repository

The implementation structure was informed by the corresponding public coursework example, but this package contains its own modelling rules, code, test inputs, and diagrams.

- Reference repository: https://github.com/Vaishakkr/FLA-Task3-PDA-CFG-Case-Studies
