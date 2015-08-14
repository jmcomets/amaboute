import pykov
from textblob import TextBlob
from history import load_latest_history, history_messages
from utils import ngrams
from tarjan import tarjan

_models = None

def generate_models(history):
    models = {}
    for nick, timed_messages in history.items():
        messages = history_messages(timed_messages)

        transitions = {}
        blob = TextBlob('\n'.join(messages))
        for a, b in blob.ngrams(n=2):
            transitions.setdefault(a, {})
            transitions[a].setdefault(b, 0)
            transitions[a][b] += 1

        normalized_transitions = {}
        for a, bs in transitions.items():
            total_bs_score = sum(bs.values())
            for b, value in bs.items():
                normalized_transitions[(a, b)] = value / total_bs_score

        chain = pykov.Chain(normalized_transitions)
        models[nick] = chain
    return models

def use_cycles(words):
    word_ngrams = list(ngrams(words, 2))
    vertices = set(word_ngrams)

    neighbor_map = {}
    for a, b in ngrams(word_ngrams, 2):
        neighbor_map.setdefault(a, set())
        neighbor_map[a].add(b)

    cycles = tarjan(vertices, lambda v: neighbor_map.get(v, []))
    cycles = list(filter(lambda c: len(c) > 1, cycles))
    if cycles:
        cycle = max(cycles, key=lambda c: len(c))
        words = []
        for word, _ in reversed(cycle):
            words.append(word)
        words.append(cycle[-1][1])
    return words

def imitate_nick(nick, amount, start=None):
    global _models
    if not _models:
        history = load_latest_history()
        _models = generate_models(history)

    # get chain if nick in models
    try:
        chain = _models[nick]
    except KeyError:
        raise ValueError('no model for nick "{}"'.format(nick))

    # generate words
    try:
        words = chain.walk(amount, start)
    except UnboundLocalError:
        raise RuntimeError('unexpected message generation failure')

    # use cycle instead of repeating
    words = use_cycles(words)

    return ' '.join(words)
