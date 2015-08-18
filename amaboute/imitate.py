import itertools
import pykov
from textblob_custom import TextBlob
from tarjan import tarjan
from history import history_messages

__all__ = ('generate_models_for_history', 'generate_model', 'imitate', 'ALL_NICKS',)

ALL_NICKS = 'amaboute'

def ngrams(xs, n):
    if n <= 1:
        raise ValueError('n should be > 1')
    ts = itertools.tee(xs, n)
    for i, t in enumerate(ts[1:]):
        for _ in range(i + 1):
            next(t, None)
    return zip(*ts)

def compute_transitions(blob, n):
    transitions = {}
    for grams in map(lambda wl: tuple(map(lambda w: w.string, wl)), blob.ngrams(n=n)):
        start, end = grams[:n-1], grams[-1]
        transitions.setdefault(start, {})
        transitions[start].setdefault(end, 0)
        transitions[start][end] += 1

    normalized_transitions = {}
    for start, ends in transitions.items():
        total_score = sum(ends.values())
        for end, value in ends.items():
            normalized_transitions[start + (end,)] = value / total_score
    return normalized_transitions

_models = {}

def generate_model(key, blob, n):
    transitions = compute_transitions(blob, n)
    chain = pykov.Chain(transitions)
    _models[key] = chain

def generate_models_for_nick(nick, messages, n):
    generate_model(nick, TextBlob('\n'.join(messages)), n)

def generate_models_for_history(history, n):
    all_messages = []

    for nick, timed_messages in history.items():
        messages = history_messages(timed_messages)
        all_messages += messages
        blob = TextBlob('\n'.join(messages))
        generate_model(nick, blob, n)

    blob = TextBlob('\n'.join(all_messages))
    generate_model(ALL_NICKS, blob, n)

def use_cycles(words, repetition_count):
    word_ngrams = list(ngrams(words, repetition_count))
    vertices = set(word_ngrams)

    neighbor_map = {}
    pairs = lambda ls: zip(ls[::2], ls[1::2])
    for a, b in pairs(word_ngrams):
        neighbor_map.setdefault(a, set())
        neighbor_map[a].add(b)

    cycles = tarjan(vertices, lambda v: neighbor_map.get(v, []))
    cycles = list(filter(lambda c: len(c) > 1, cycles))
    if cycles:
        cycle = max(cycles, key=lambda c: len(c))
        words = []
        for node in reversed(cycle):
            word = node[0]
            words.append(word)
        words.append(cycle[-1][1])
    return words

def imitate(nick, amount, start=None, repetition_count=3):
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
    words = use_cycles(words, repetition_count)

    return ' '.join(words)
