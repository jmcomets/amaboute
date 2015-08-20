import itertools
from asyncio import get_event_loop, coroutine
from concurrent.futures import ThreadPoolExecutor

from markovify import split_into_sentences
from markovify.text import NewlineText

from history import history_messages

__all__ = ('index_models_for_history', 'index_model_for_nick',
           'generate_imitation', 'Error', 'NickNotIndexed',)

ALL_NICKS = 'amaboute'

_models = {}

flatten = itertools.chain.from_iterable

class HistoryText(NewlineText):
    def __init__(self, text, n=2):
        super().__init__(text, state_size=n)

    def sentence_split(self, text):
        sentences =  super().sentence_split(text)
        return list(flatten(map(split_into_sentences, sentences)))

def index_model_for_nick(nick, text, n):
    if type(text) != str:
        text = '\n'.join(text)
    _models[nick] = HistoryText(text, n)

def index_models_for_history(history, n):
    all_messages = []
    for nick, timed_messages in history.items():
        messages = list(history_messages(timed_messages))
        all_messages += messages
        index_model_for_nick(nick, messages, n)
    index_model_for_nick(ALL_NICKS, all_messages, n)

_executor = ThreadPoolExecutor(max_workers=2)

@coroutine
def generate_imitation(nick, nb_tries=10):
    try:
        model = _models[nick]
    except KeyError as e:
        raise NickNotIndexed('no model for nick "{}"'.format(nick)) from e
    else:
        loop = get_event_loop()
        for _ in range(nb_tries):
            imitation = yield from loop.run_in_executor(_executor, model.make_sentence)
            if imitation is not None:
                return imitation
        raise RuntimeError('imitation generation failure')

class Error(Exception): pass

class NickNotIndexed(Error, ValueError):
    def __init__(self, nick):
        self.nick = nick

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('no nick given', file=sys.stderr)
        sys.exit(1)
    nick = sys.argv[1]

    def main():
        from history import load_latest_history
        from dictionaries import load_datasets

        n = 2
        history = load_latest_history()

        if nick == ALL_NICKS:
            index_models_for_history(history, n)
        else:
            try:
                timed_messages = history[nick]
            except KeyError:
                for dataset_nick, dataset in load_datasets():
                    if dataset_nick == nick:
                        messages = dataset
            else:
                messages = history_messages(timed_messages)
            index_model_for_nick(nick, messages, n)

        for _ in range(10):
            sentence = yield from generate_imitation(nick)
            print(sentence)

    loop = get_event_loop()
    loop.run_until_complete(main())
    loop.close()
