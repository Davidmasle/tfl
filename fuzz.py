import random
import re
from collections import Counter

class RewriteSystem:
    def __init__(self, rules, alphabet=None, name="SRS"):
        self.rules = rules
        self.alphabet = alphabet or []
        self.name = name
        self._closure_cache = {}

    def apply_rules_once(self, word):
        results = set()
        for lhs, rhs in self.rules:
            for match in re.finditer(f"(?={re.escape(lhs)})", word):
                start = match.start()
                new_word = word[:start] + rhs + word[start+len(lhs):]
                results.add(new_word)
        return results

    def _bfs(self, start, target_set=None):
        if target_set is None and start in self._closure_cache:
            return self._closure_cache[start]
        seen = {start}
        frontier = [start]
        while frontier:
            new_frontier = []
            for w in frontier:
                for nw in self.apply_rules_once(w):
                    if nw not in seen:
                        if target_set and nw in target_set:
                            return True
                        seen.add(nw)
                        new_frontier.append(nw)
            frontier = new_frontier

        if target_set is None:
            self._closure_cache[start] = seen
        return True if target_set else seen

    def closure(self, start):
        return self._bfs(start)

    def is_reach(self, start, target_set):
        return self._bfs(start, target_set)

class Experiment:
    def __init__(self, system_main, system_check, alphabet, word_length=17, steps=8):
        self.system_main = system_main
        self.system_check = system_check
        self.alphabet = alphabet
        self.word_length = word_length
        self.steps = steps
        self.rng = random.SystemRandom()

    def rand_word(self):
        return "".join(self.rng.choices(self.alphabet, k=self.word_length))

    def apply_rand_rules(self, word):
        for _ in range(self.steps):
            matches = [(i, lhs, rhs)
                          for lhs, rhs in self.system_main.rules
                          for i in range(len(word) - len(lhs) + 1)
                          if word[i:i+len(lhs)] == lhs]
            if not matches:
                continue
            i, lhs, rhs = self.rng.choice(matches)
            word = word[:i] + rhs + word[i+len(lhs):]
        return word

    def generate_tests(self, n_tests=5):
        for _ in range(n_tests):
            word = self.rand_word()
            rewritten_word = self.apply_rand_rules(word)

            if len(word) <= len(rewritten_word):
                equivalent = self.system_check.is_reach(word, self.system_check.closure(word))
            else:
                equivalent = self.system_check.is_reach(rewritten_word, self.system_check.closure(rewritten_word))

            yield (word, rewritten_word, equivalent)

    def run_tests_summary(self, n_tests=5):
        counter = Counter()
        for word, rewritten_word, equivalent in self.generate_tests(n_tests):
            print("Исходное слово:", word)
            print("Переписанное слово:", rewritten_word)
            print(f"{self.system_check.name}: {equivalent}\n")
            counter['total'] += 1
            counter['success' if equivalent else 'failure'] += 1
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

T1 = [
    ("aa", "a"),
    ("bb", "a"),
    ("ab", "a"),
    ("ba", "a"),
]

alphabet = ["a", "b"]

system_main = RewriteSystem(T, alphabet, name="T")
system_check = RewriteSystem(T1, alphabet, name="T1")

experiment = Experiment(system_main, system_check, alphabet, word_length=20, steps=8)

for word, rewritten_word, eq in experiment.generate_tests(n_tests=5):
    pass

summary = experiment.run_tests_summary(n_tests=5)
print(summary)
