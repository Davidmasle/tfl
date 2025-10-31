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

def invariant_length_growth_limited(prev, curr):
    return len(curr) <= len(prev) * 2

def invariant_ab_ba_blocks(prev, curr):
    count_prev = sum(prev[i:i+length] in ['ab','ba'] 
                     for length in [3,4] for i in range(len(prev)-length+1))
    count_curr = sum(curr[i:i+length] in ['ab','ba'] 
                     for length in [3,4] for i in range(len(curr)-length+1))
    return count_curr <= count_prev + 1


experiment = Experiment(system_main, alphabet, word_length=20, steps=8)
summary = experiment.run_metamorphic_tests(
    n_tests=100000,
    invariants=[invariant_length_growth_limited, invariant_ab_ba_blocks]
)
print(summary)
