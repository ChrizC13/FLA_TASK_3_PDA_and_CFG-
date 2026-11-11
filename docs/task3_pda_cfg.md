# Task 3 - PDA and CFG case studies

## 1. Balanced delimiters

CFG:

```text
S -> ( S ) S | [ S ] S | { S } S | epsilon
```

The PDA pushes each opener. A closer can be consumed only when it matches the stack top; the matching opener is popped. A right-end marker is appended by the simulator. It transitions to the final state only with the bottom marker exposed.

## 2. Arithmetic expressions

Ambiguous grammar for analysis:

```text
E -> E + E | E * E | ( E ) | id
```

For `id+id*id`, this permits both `id+(id*id)` and `(id+id)*id`. With values 2, 3, 4, the interpretations evaluate to 14 and 20.

Revised precedence grammar:

```text
E  -> T E'
E' -> + T E' | epsilon
T  -> F T'
T' -> * F T' | epsilon
F  -> ( E ) | id
```

The LL(1) parser expands grammar variables and matches terminals using a stack. This is a deterministic PDA-style parser for the supported operators.

## 3. Binary palindromes

CFG:

```text
P -> 0 P 0 | 1 P 1 | 0 | 1 | epsilon
```

For `w#reverse(w)`, the marker identifies the midpoint, so the DPDA pushes the prefix and then pops matching suffix symbols. For the unmarked even-length language `ww^R`, the NPDA uses an epsilon transition to guess the split position.

## Determinism summary

| Case | Machine | Determinism |
|---|---|---|
| Balanced delimiters | PDA | Deterministic |
| Precedence expression grammar | Predictive PDA | Deterministic |
| Marked palindrome | PDA | Deterministic |
| Unmarked even palindrome | PDA | Nondeterministic |

The NPDA simulator uses breadth-first search over configurations and enforces a configurable maximum configuration count to prevent unbounded exploration.
