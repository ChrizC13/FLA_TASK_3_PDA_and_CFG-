"""A bounded breadth-first simulator for small pushdown automata."""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Transition:
    source: str
    input_symbol: str | None  # None denotes epsilon
    stack_top: str
    target: str
    replacement: str         # bottom-to-top replacement for stack_top
    label: str = ""


@dataclass
class PDAResult:
    accepted: bool
    path: list[tuple[str, int, tuple[str, ...], str]]
    explored: int
    reason: str


class PDA:
    def __init__(self, states: Iterable[str], input_alphabet: Iterable[str], stack_alphabet: Iterable[str],
                 transitions: Iterable[Transition], start: str, initial_stack: str,
                 final_states: Iterable[str], name: str = "PDA"):
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.stack_alphabet = set(stack_alphabet)
        self.transitions = list(transitions)
        self.start = start
        self.initial_stack = initial_stack
        self.final_states = set(final_states)
        self.name = name
        self._index: dict[tuple[str, str | None, str], list[Transition]] = {}
        for transition in self.transitions:
            key = (transition.source, transition.input_symbol, transition.stack_top)
            self._index.setdefault(key, []).append(transition)

    def is_deterministic(self) -> bool:
        for state in self.states:
            for top in self.stack_alphabet:
                eps = self._index.get((state, None, top), [])
                consuming = [symbol for symbol in self.input_alphabet
                             if self._index.get((state, symbol, top), [])]
                if len(eps) > 1 or any(len(self._index.get((state, sym, top), [])) > 1 for sym in self.input_alphabet):
                    return False
                if eps and consuming:
                    return False
        return True

    def simulate(self, value: str, end_marker: str = "⊣", max_configurations: int = 50000) -> PDAResult:
        stream = value + end_marker
        start_config = (self.start, 0, (self.initial_stack,))
        queue = deque([start_config])
        previous: dict[tuple[str, int, tuple[str, ...]], tuple[tuple[str, int, tuple[str, ...]], str] | None] = {start_config: None}
        explored = 0
        accepted_config = None
        while queue:
            config = queue.popleft()
            state, position, stack = config
            explored += 1
            if position == len(stream) and state in self.final_states:
                accepted_config = config
                break
            if explored > max_configurations:
                return PDAResult(False, [], explored, f"configuration limit ({max_configurations}) reached")
            if not stack:
                continue
            top = stack[-1]
            candidates: list[Transition] = []
            candidates.extend(self._index.get((state, None, top), []))
            if position < len(stream):
                candidates.extend(self._index.get((state, stream[position], top), []))
            for transition in candidates:
                next_position = position + (transition.input_symbol is not None)
                next_stack = stack[:-1] + tuple(transition.replacement)
                next_config = (transition.target, next_position, next_stack)
                if next_config not in previous:
                    label = transition.label or f"{transition.input_symbol or 'ε'}; {top}→{transition.replacement or 'ε'}"
                    previous[next_config] = (config, label)
                    queue.append(next_config)
        if accepted_config is None:
            return PDAResult(False, [], explored, "no accepting configuration was reached")
        reverse_path: list[tuple[str, int, tuple[str, ...], str]] = []
        current = accepted_config
        while current is not None:
            back = previous[current]
            action = "START" if back is None else back[1]
            reverse_path.append((current[0], current[1], current[2], action))
            current = None if back is None else back[0]
        reverse_path.reverse()
        return PDAResult(True, reverse_path, explored, "accepting configuration reached")

    def to_dot(self, title: str | None = None) -> str:
        lines = ["digraph PDA {", 'rankdir="LR";', f'graph [label="{title or self.name}", labelloc="t", fontsize=18];',
                 'node [shape=circle, style=filled, fillcolor="#EAF2F8", color="#315A78", fontname="Arial"];',
                 'edge [fontname="Arial", color="#526D82"];', 'start [shape=point, label=""];',
                 f'start -> "{self.start}";']
        for state in sorted(self.states):
            shape = "doublecircle" if state in self.final_states else "circle"
            fill = "#D5F5E3" if state in self.final_states else "#EAF2F8"
            lines.append(f'"{state}" [shape={shape}, fillcolor="{fill}"];')
        grouped: dict[tuple[str, str], list[str]] = {}
        for transition in self.transitions:
            label = f"{transition.input_symbol or 'ε'}, {transition.stack_top} → {transition.replacement or 'ε'}"
            grouped.setdefault((transition.source, transition.target), []).append(label)
        for (source, target), labels in sorted(grouped.items()):
            label_text = '; '.join(labels)
            lines.append(f'"{source}" -> "{target}" [label="{label_text}"];')
        lines.append("}")
        return "\n".join(lines)


def make_bracket_dpda() -> PDA:
    """DPDA for correctly nested (), [] and {}; ⊣ is an explicit right end-marker."""
    marker = "Z"
    openers = "([{"
    closers = {")": "(", "]": "[", "}": "{"}
    stack_tops = [marker, *openers]
    transitions: list[Transition] = []
    for top in stack_tops:
        for opener in openers:
            transitions.append(Transition("q", opener, top, "q", top + opener,
                                          f"read {opener}; push {opener}"))
    for closer, opener in closers.items():
        transitions.append(Transition("q", closer, opener, "q", "",
                                      f"read {closer}; pop {opener}"))
    transitions.append(Transition("q", "⊣", marker, "qf", marker, "end marker with empty nesting stack"))
    return PDA({"q", "qf"}, set("()[]{}⊣"), set(stack_tops), transitions,
               "q", marker, {"qf"}, "Balanced-bracket DPDA")


def make_marked_palindrome_dpda() -> PDA:
    """DPDA for w#reverse(w), where # explicitly marks the midpoint."""
    marker = "Z"
    tops = [marker, "0", "1"]
    transitions: list[Transition] = []
    for top in tops:
        for bit in "01":
            transitions.append(Transition("push", bit, top, "push", top + bit, f"push {bit}"))
        transitions.append(Transition("push", "#", top, "pop", top, "centre marker #"))
    for bit in "01":
        transitions.append(Transition("pop", bit, bit, "pop", "", f"match {bit}; pop"))
    transitions.append(Transition("pop", "⊣", marker, "qf", marker, "all mirrored symbols matched"))
    return PDA({"push", "pop", "qf"}, set("01#⊣"), set(tops), transitions,
               "push", marker, {"qf"}, "Marked-palindrome DPDA")


def make_even_palindrome_npda() -> PDA:
    """NPDA for even-length binary palindromes ww^R; epsilon guesses the midpoint."""
    marker = "Z"
    tops = [marker, "0", "1"]
    transitions: list[Transition] = []
    for top in tops:
        for bit in "01":
            transitions.append(Transition("push", bit, top, "push", top + bit, f"push {bit}"))
            transitions.append(Transition("pop", bit, bit, "pop", "", f"match {bit}; pop"))
        transitions.append(Transition("push", None, top, "pop", top, "guess midpoint (epsilon)"))
    transitions.append(Transition("pop", "⊣", marker, "qf", marker, "stack returned to bottom marker"))
    return PDA({"push", "pop", "qf"}, set("01⊣"), set(tops), transitions,
               "push", marker, {"qf"}, "Unmarked even-palindrome NPDA")
