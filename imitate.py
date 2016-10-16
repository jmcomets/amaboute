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

if __name__ == '__main__':
    import sys

    from models import get_registered_profiles

    registered_profiles = get_registered_profiles()
    registered_nicknames = set(map(lambda p: p.nickname, registered_profiles))

    if len(sys.argv) < 2:
        print('No nickname given', file=sys.stderr)
        if registered_nicknames:
            print('Choose one of:', file=sys.stderr)
            print('\n'.join(map(lambda n: '* %s' % n, registered_nicknames)), file=sys.stderr)
        sys.exit(1)
    nickname = sys.argv[1]

    if nickname not in registered_nicknames:
        print('Invalid nickname given', file=sys.stderr)
        if registered_nicknames:
            print('Choose one of:', file=sys.stderr)
            print('\n'.join(map(lambda n: '* %s' % n, registered_nicknames)), file=sys.stderr)
        sys.exit(1)

    n = 2
    if len(sys.argv) > 2:
        try:
            n = int(sys.argv[2])
            if n <= 0:
                raise ValueError
        except ValueError:
            print('N should be a positive integer', file=sys.stderr)

    profiles_by_nickname = dict(map(lambda p: (p.nickname, p), registered_profiles))
    messages = list(map(lambda m: m.text, profiles_by_nickname[nickname].messages))

    imitator = Imitator(messages)
    imitator.index(2)
    print(imitator.generate_sentence())
