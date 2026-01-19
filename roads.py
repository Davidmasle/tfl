from collections import deque

rules = [
    ("aaaa", "ab"),
    ("abbb", "bba"),
    ("babb", "bb"),
    ("aabb", "aaba"),
    ("bbbaa", "bb"),
    ("aaabab", "baabb"),
    ("baabb", "aabab"),
    ("baabab", "bab"),
    ("bbabab", "bb"),
    ("baabaab", "a"),
    ("bab", "baaaab"),
]

def find_all_substring_indices(word, sub):
    indices = []
    i = 0
    while i <= len(word) - len(sub):
        if word[i:i+len(sub)] == sub:
            indices.append(i)
        i += 1
    return indices

def reduce_with_path(start_word):
    

    queue = deque()
    queue.append((start_word, []))
    seen = set()

    while queue:
        word, path = queue.popleft()
        if word in seen:
            continue
        seen.add(word)

        if word == "a": #or word =="bb":
            path.append((word, "norm", None))
            return path

        for a, b in rules:
            for idx in find_all_substring_indices(word, a):
                new_word = word[:idx] + b + word[idx+len(a):]
                queue.append((new_word, path + [(word, f"{a} → {b}", idx)]))
            for idx in find_all_substring_indices(word, b):
                new_word = word[:idx] + a + word[idx+len(b):]
                queue.append((new_word, path + [(word, f"{b} → {a}", idx)]))
    return None

word_to_test = "bb"
path = reduce_with_path(word_to_test)

if path:
    for step in path:
        word, action, idx = step
        if action == "norm":
            print(f"Нормальная форма достигнута: {word}")
        else:
            print(f"{word} → ({action} на позиции {idx})")
else:
    print(f"Слово '{word_to_test}' не сводится к нормальной форме")



