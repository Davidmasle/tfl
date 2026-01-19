import random
import re
from collections import Counter

class RewriteSystem:
    def __init__(self, rules, alphabet=None, name="SRS"):
        self.rules = rules
        self.alphabet = alphabet or []
        self.name = name
        
    def apply_rules_once(self, word):
        results = set()
        for lhs, rhs in self.rules:
            for match in re.finditer(f"(?={re.escape(lhs)})", word):
                start = match.start()
                new_word = word[:start] + rhs + word[start+len(lhs):]
                results.add(new_word)
        return results

    def apply_random_steps(self, word, steps=8):
        rng = random.SystemRandom()
        for _ in range(steps):
            matches = [(i, lhs, rhs)
                       for lhs, rhs in self.rules
                       for i in range(len(word)-len(lhs)+1)
                       if word[i:i+len(lhs)] == lhs]
            if not matches:
                break
            i, lhs, rhs = rng.choice(matches)
            word = word[:i] + rhs + word[i+len(lhs):]
        return word

class Experiment:
    def __init__(self, system, alphabet, word_length=17, steps=8):
        self.system = system
        self.alphabet = alphabet
        self.word_length = word_length
        self.steps = steps
        self.rng = random.SystemRandom()

    def rand_word(self):
        return "".join(self.rng.choices(self.alphabet, k=self.word_length))

    def run_metamorphic_tests(self, n_tests=10, invariants=None):
        invariants = invariants or []
        counter = Counter()
        for _ in range(n_tests):
            word = self.rand_word()
            rewritten = self.system.apply_random_steps(word, self.steps)
            success = True
            for inv in invariants:
                if not inv(word, rewritten):
                    success = False
                    print("Не прошел инвариант:", inv.__name__)
            counter['total'] += 1
            counter['success' if success else 'failure'] += 1
        return counter


T = [
    ("aaaa", "ab"),
    ("abbb", "bba"),
    ("babb", "bb"),
    ("aabb", "aaba"),
    ("bbbaa", "bb"),
    ("aaabab", "baabb"),
    ("baabb", "aabab"),
    ("baabab", "bab"),
    ("bbabab", "bb"),
    ("bab", "baaaab"),
    ("baabaab", "a"),
]

alphabet = ["a", "b"]
system_main = RewriteSystem(T, alphabet, name="T")

def N(s, w):
    L = len(s)
    return sum(1 for i in range(len(w)-L+1) if w[i:i+L] == s)

def J(w):
    return (N("b", w) + N("ab", w) + N("ba", w) + N("aba", w) + N("abb", w) + N("bba", w) + N("bbb", w)) % 2

def inv_J(start, end):
    return J(start) == J(end)

def K(w):
    return (-2*N("a", w) - N("b", w) + 2*N("aa", w) + N("ab", w) + N("ba", w) 
            + N("aba", w) + N("abb", w) + N("bba", w) + N("bbb", w))

def inv_K(start, end):
    return K(start) == K(end)

experiment = Experiment(system_main, alphabet, word_length=12, steps=8)
summary = experiment.run_metamorphic_tests(
    n_tests=100000,
    invariants=[inv_J, inv_K],
    )
print(summary)
