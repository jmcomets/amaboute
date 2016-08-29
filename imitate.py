import itertools as it

from markovify import split_into_sentences
from markovify.text import NewlineText

class NotIndexed(RuntimeError):
    pass

class Imitator:
    def __init__(self, messages=None):
        if messages is None:
            messages = []
        self.messages = list(messages)
        self.model = None

    def add_message(self, message):
        self.messages.append(message)

    def generate_sentence(self, nb_tries=10):
        if self.model is None:
            raise NotIndexed
        for _ in range(nb_tries):
            imitation = self.model.make_sentence()
            if imitation is not None:
                return imitation
        return None

    def index(self, n):
        self.model = MessagesModel(self.messages, n)

class MessagesModel(NewlineText):
    def __init__(self, messages, n):
        super().__init__('\n'.join(messages), state_size=n)

    def sentence_split(self, text):
        sentences =  super().sentence_split(text)
        return list(it.chain.from_iterable(map(split_into_sentences, sentences)))
