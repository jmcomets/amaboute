import itertools
from asyncio import get_event_loop, coroutine
from concurrent.futures import ThreadPoolExecutor
from markovify.text import NewlineText
from history import history_messages

__all__ = ('index_models_for_history', 'index_model_for_nick',
           'generate_imitation', 'Error', 'NickNotIndexed',)

ALL_NICKS = 'amaboute'

_models = {}

flatten = itertools.chain.from_iterable

class HistoryText(NewlineText):
    def __init__(self, messages, n=2):
        super().__init__(messages, state_size=n)

    def sentence_split(self, messages):
        return super().sentence_split('\n'.join(messages))

def index_model_for_nick(nick, messages, n):
    if type(messages) != list:
        messages = list(messages)
    _models[nick] = HistoryText(messages, n)

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
    def main():
        #from dictionaries import load_datasets
        #nick, dataset = next(load_datasets())
        #index_model_for_nick(nick, [dataset], 2)

        from history import load_latest_history
        nick = 'etkadt'
        history = load_latest_history()
        timed_messages = history[nick]
        messages = history_messages(timed_messages)
        index_model_for_nick(nick, messages, 2)

        for _ in range(10):
            sentence = yield from generate_imitation(nick)
            print(sentence)

    loop = get_event_loop()
    loop.run_until_complete(main())
    loop.close()
