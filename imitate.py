import itertools
import pykov
from textblob import TextBlob
from tarjan import tarjan
from history import history_messages

__all__ = ('generate_models_for_history', 'generate_model_for_nick',
           'imitate', 'Error', 'InvalidFirstWord',)

ALL_NICKS = 'amaboute'

def ngrams(xs, n):
    if n <= 1:
        raise ValueError('n should be > 1')
    ts = itertools.tee(xs, n)
    for i, t in enumerate(ts[1:]):
        for _ in range(i + 1):
            next(t, None)
    return zip(*ts)

pairs = lambda ls: zip(ls[::2], ls[1::2])
flatten = itertools.chain.from_iterable

_models = {}

def message_tokens(message, n):
    blob = TextBlob(message)
    for grams in blob.ngrams(n):
        yield tuple(word.string for word in grams)

def generate_model_for_nick(nick, messages, n):
    transitions = {}

    for message in messages:
        for grams in message_tokens(message, n):
            start, end = grams[:n-1], grams[-1]
            transitions.setdefault(start, {})
            transitions[start].setdefault(end, 0)
            transitions[start][end] += 1

    normalized_transitions = {}
    for start, ends in transitions.items():
        total_score = sum(ends.values())
        for end, value in ends.items():
            normalized_transitions[start + (end,)] = value / total_score

    _models[nick] = pykov.Chain(normalized_transitions)

def generate_models_for_history(history, n):
    all_messages = []
    for nick, timed_messages in history.items():
        messages = history_messages(timed_messages)
        all_messages += messages
        generate_model_for_nick(nick, messages, n)
    generate_model_for_nick(ALL_NICKS, all_messages, n)

def cut_cycles(words, repetition_count):
    word_ngrams = list(ngrams(words, repetition_count))
    vertices = set(word_ngrams)

    neighbor_map = {}
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

def imitate(nick, amount, start=None, repetition_count=2, nb_tries=10):
    try:
        chain = _models[nick]
    except KeyError as e:
        raise NickNotIndexed('no model for nick "{}"'.format(nick)) from e

    for _ in range(nb_tries):
        try:
            words = chain.walk(amount, start)
        except KeyError as e:
            raise InvalidFirstWord(start) from e
        except UnboundLocalError:
            pass # this is why there's multiple tries
        else:
            if repetition_count is not None:
                words = cut_cycles(words, repetition_count)
            return ' '.join(words)
    raise RuntimeError('unexpected message generation failure')

class Error(Exception): pass

class InvalidFirstWord(Error, ValueError):
    def __init__(self, first_word):
        self.first_word = first_word

class NickNotIndexed(Error, ValueError):
    def __init__(self, nick):
        self.nick = nick

if __name__ == '__main__':
    from dictionaries import load_datasets
    nick, dataset = next(load_datasets())
    generate_model_for_nick(nick, [dataset], 4)
    #from history import load_latest_history
    #nick = 'etkadt'
    #history = load_latest_history()
    #timed_messages = history[nick]
    #messages = history_messages(timed_messages)
    #generate_model_for_nick(nick, messages, 3)
    print(imitate(nick, 10))
