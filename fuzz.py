import random
import re
from collections import defaultdict
from dataclasses import dataclass

ALPHABET = ("a", "b", "c")

def parse_edges(text: str):
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        a, b, c = line.split()
        yield int(a), b, int(c)


@dataclass(frozen=True)
class DFA:
    start: int
    trans: dict[int, dict[str, int]]   
    finals: set[int]
    name: str = "DFA"

    def run(self, word: str) -> tuple[int, bool]:
        state = self.start
        for ch in word:
            state = self.trans.get(state, {}).get(ch, -1)
            if state == -1:
                return -1, False
        return state, state in self.finals


def build_min_dfa() -> DFA:
    finals = {5, 8, 10, 12, 24, 33, 34, 35, 36, 39, 40}

    dfa_edges = r"""
    0 a 1
    0 b 2
    0 c 3

    1 a 4
    1 b 5
    1 c 6
    2 a 7
    2 b 8
    2 c 6
    3 a 9
    3 b 10
    3 c 11

    4 a 9
    4 b 12
    4 c 6
    5 a 13
    5 b 14
    5 c 6

    6 a 6
    6 b 6
    6 c 6

    7 a 15
    7 b 10
    7 c 6
    8 a 16
    8 b 17
    8 c 3

    9 a 9
    9 b 10
    9 c 6

    10 a 13
    10 b 18
    10 c 6
    11 a 19
    11 b 20
    11 c 3

    12 a 21
    12 b 18
    12 c 6
    13 a 22
    13 b 6
    13 c 6

    14 a 1
    14 b 20
    14 c 23
    15 a 19
    15 b 24
    15 c 3

    16 a 25
    16 b 10
    16 c 6
    17 a 9
    17 b 8
    17 c 26

    18 a 6
    18 b 6
    18 c 26
    19 a 4
    19 b 10
    19 c 6

    20 a 9
    20 b 8
    20 c 6
    21 a 27
    21 b 28
    21 c 9

    22 a 6
    22 b 29
    22 c 6
    23 a 30
    23 b 10
    23 c 31

    24 a 32
    24 b 33
    24 c 6
    25 a 9
    25 b 34
    25 c 6

    26 a 22
    26 b 6
    26 c 26
    27 a 4
    27 b 35
    27 c 6

    28 a 19
    28 b 36
    28 c 9
    29 a 6
    29 b 6
    29 c 10

    30 a 9
    30 b 35
    30 c 6
    31 a 27
    31 b 20
    31 c 23

    32 a 37
    32 b 10
    32 c 6
    33 a 16
    33 b 17
    33 c 23

    34 a 21
    34 b 18
    34 c 10
    35 a 13
    35 b 18
    35 c 10

    36 a 38
    36 b 39
    36 c 6
    37 a 19
    37 b 40
    37 c 3

    38 a 30
    38 b 10
    38 c 6
    39 a 13
    39 b 18
    39 c 26

    40 a 32
    40 b 33
    40 c 10
    """

    trans = defaultdict(dict)
    for s, ch, t in parse_edges(dfa_edges):
        trans[s][ch] = t

    return DFA(start=0, trans=dict(trans), finals=finals)


@dataclass
class NFA:
    start: int
    finals: set[int]
    trans: dict[tuple[int, str], set[int]]
    eps: dict[int, set[int]]
    name: str = "NFA"

    def eps_closure(self, states: set[int]) -> set[int]:
        stack = list(states)
        closure = set(states)
        while stack:
            s = stack.pop()
            for t in self.eps.get(s, ()):
                if t not in closure:
                    closure.add(t)
                    stack.append(t)
        return closure

    def step(self, cur: set[int], ch: str) -> set[int]:
        nxt = set().union(*(self.trans.get((s, ch), ()) for s in cur))
        return self.eps_closure(nxt) if nxt else set()

    def run(self, word: str) -> bool:
        cur = self.eps_closure({self.start})
        for ch in word:
            cur = self.step(cur, ch)
            if not cur:
                return False
        return bool(cur & self.finals)


def build_nfa_from_edges(edges_text: str, *, start: int, finals: set[int], name="NFA") -> NFA:
    trans = defaultdict(set)
    eps = defaultdict(set)
    for s, sym, t in parse_edges(edges_text):
        if sym == "e":
            eps[s].add(t)
        else:
            trans[(s, sym)].add(t)
    return NFA(start=start, finals=finals, trans=dict(trans), eps=dict(eps), name=name)


def build_nfa() -> NFA:
    nfa_edges = r"""
    0 b 1
    0 a 4
    0 e 7

    1 a 2
    4 b 5

    7 b 8
    8 b 7
    7 e 10
    7 c 9
    9 c 7

    10 a 11
    10 a 15
    10 b 15
    10 c 15

    2 a 3
    3 b 1
    3 e 7

    5 b 6
    6 e 7
    6 a 4

    11 a 12
    12 b 13
    13 a 14
    13 a 10
    14 b 10

    15 a 15
    15 b 16

    16 b 17
    17 c 18
    18 c 18
    18 a 20

    16 a 19
    19 a 20
    20 b 21
    21 c 16
    """
    return build_nfa_from_edges(nfa_edges, start=0, finals={16}, name="NFA")


@dataclass
class PKA:
    core: NFA
    acc1: set[int]
    acc2: set[int]
    name: str = "PKA"

    def run(self, word: str) -> bool:
        cur = self.core.eps_closure({self.core.start})
        for ch in word:
            cur = self.core.step(cur, ch)
            if not cur:
                return False
        return bool(cur & self.acc1) and bool(cur & self.acc2)


def build_pka() -> PKA:
    pka_edges = r"""
    25 e 0
    25 e 22

    0 b 1
    0 a 4
    0 e 7
    1 a 2
    4 b 5

    7 b 8
    8 b 7
    7 e 10
    7 c 9
    9 c 7

    10 a 11
    10 a 15
    10 b 15
    10 c 15

    2 a 3
    3 b 1
    3 e 7
    5 b 6
    6 e 7
    6 a 4

    11 a 12
    12 b 13
    13 a 14
    13 a 10
    14 b 10

    15 a 15
    15 b 16

    16 b 17
    17 c 18
    18 c 18
    18 a 20
    16 a 19
    19 a 20
    20 b 21
    21 c 16

    22 a 23
    23 a 23
    23 b 24
    23 c 24
    22 b 24
    22 c 24

    24 a 23
    24 b 24
    24 c 24
    """
    core = build_nfa_from_edges(
        pka_edges,
        start=25,
        finals={16, 24},
        name="PKA",
    )
    return PKA(core=core, acc1={16}, acc2={24})

@dataclass
class Experiment:
    dfa: DFA
    nfa: NFA
    pka: PKA
    regex: re.Pattern
    n_tests: int = 10000
    max_len: int = 30
    seed: int | None = None

    def __post_init__(self):
        self.rng = random.SystemRandom()

    def random_word(self, length: int) -> str:
        return "".join(self.rng.choice(ALPHABET) for _ in range(length))

    def verdicts(self, word: str) -> dict[str, bool]:
        _, dfa_ok = self.dfa.run(word)
        return {
            self.dfa.name: dfa_ok,
            self.nfa.name: self.nfa.run(word),
            self.pka.name: self.pka.run(word),
            "RE": bool(self.regex.fullmatch(word)),
        }

    def run(self):
        for length in range(1, self.max_len):
            for k in range(self.n_tests):
                word = self.random_word(length)
                v = self.verdicts(word)

                if len(set(v.values())) != 1:
                    _, is_in_dfa = self.dfa.run(word)
                    is_in_nfa = self.nfa.run(word)
                    is_in_pka = self.pka.run(word)
                    is_in_re = bool(self.regex.fullmatch(word))

                    raise AssertionError(
                        "Расхождение\n"
                        f"length={length}, test={k+1}\n"
                        f"word={word!r}\n"
                        f"DFA : {is_in_dfa}\n"
                        f"NFA : {is_in_nfa}\n"
                        f"PKA : {is_in_pka}\n"
                        f"RE  : {is_in_re}\n"
                    )
        print("All tests passed.")


def main():
    reg = r'^((baa)*|(abb)*)(bb|cc)*(aa(ba|bab))*(a|b|c)a*b((a|bcc*)abc)*$'
    exp = Experiment(
        dfa=build_min_dfa(),
        nfa=build_nfa(),
        pka=build_pka(),
        regex=re.compile(reg),
    )
    exp.run()

if __name__ == "__main__":
    main()
