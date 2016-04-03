import sys
import time
import logging

from history import load_latest_history, save_history, history_messages
from imitate import (generate_imitation, index_model_for_nick,
                     index_models_for_history, NickNotIndexed)

class BaseBot:
    def __init__(self, channel, admin):
        self.history = {}
        self.channel = channel
        self.admin = admin
        self.bot = None

    def send_message(self, target, message):
        raise NotImplementedError

    def send_message_to_channel(self, message):
        self.send_message(self.channel, message)

    def send_message_to_admin(self, message):
        self.send_message(self.admin, message)

    def on_message(self, target, nick, message):
        if target == self.channel and not message.startswith('!') and not message.startswith('/'):
            logging.debug('logged message [{}]: {}'.format(nick, message))
            self.history.setdefault(nick, [])
            self.history[nick].append((time.time(), message))

    def index_models(self, sender, nick=None, n=None):
        if n is None:
            n = 2
        else:
            try:
                n = validate_n(n)
            except ValueError as e:
                self.send_message(sender, str(e))
                return

        if nick:
            try:
                timed_messages = self.history[nick]
            except KeyError:
                self.send_message_to_admin('no history for nick {}'.format(nick))
            else:
                messages = history_messages(timed_messages)
                logging.info('indexing for {}'.format(nick))
                index_model_for_nick(nick, messages, n)
        else:
            logging.info('indexing all models')
            self.index_all(n)

    def imitate_nick(self, target, sender, nick):
        try:
            logging.info('generating an imitation for {}'.format(nick))
            message = generate_imitation(nick)
        except NickNotIndexed as e:
            self.send_message(sender, 'nick not indexed {}'.format(e.nick))
        except RuntimeError as e:
            self.send_message_to_admin(str(e))
            print(e, file=sys.stderr)
        else:
            self.send_message_to_channel('< {} ({})> {}'.format(nick, sender, message))

    def index_all(self, n=2):
        if self.history:
            logging.info('indexing all models with {}-grams'.format(n))
            index_models_for_history(self.history, n)

    def load_latest_history(self):
        try:
            self.history = load_latest_history()
        except IOError as e:
            self.send_message_to_admin(str(e))

    def save_history(self):
        if self.history:
            filename = save_history(self.history)
            nb_nicks = len(self.history)
            nb_messages = sum(len(messages) for messages in self.history.values())
            self.send_message_to_admin('saved {} messages from {} nicks to {}'.format(
                nb_messages, nb_nicks, filename))

def validate_n(n):
    try:
        n = int(n)
    except ValueError as e:
        raise ValueError('invalid n {}, should be an integer'.format(n)) from e
    else:
        available_ns = [2, 3]
        if n not in available_ns:
            raise ValueError('invalid n, available are: {}'.format(available_ns))
        return n
