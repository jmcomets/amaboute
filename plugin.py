import sys
import time
from asyncio import coroutine

import irc3
from irc3.plugins.command import command
from irc3.plugins.cron import cron

from history import load_latest_history, save_history, history_messages
from imitate import generate_imitation, index_model_for_nick, index_models_for_history, NickNotIndexed

@irc3.plugin
class Plugin:
    ADMIN = 'jmcomets'
    CHANNEL = '#insa-if'

    def __init__(self, bot):
        self.bot = bot
        self.history = {}

    def send_message(self, target, message):
        self.bot.privmsg(target, message)

    def send_message_to_channel(self, message):
        self.send_message(self.CHANNEL, message)

    def send_message_to_admin(self, message):
        self.send_message(self.ADMIN, message)

    @command(permission='admin')
    def message(self, mask, data, args):
        """Send a message.
            %%message [<message>...]
        """
        self.send_message_to_channel(' '.join(args['<message>']))

    @command(permission='admin')
    def load(self, mask, data, args):
        """Load the state from a file.
            %%load
        """
        try:
            self.history = load_latest_history()
        except IOError as e:
            self.send_message_to_admin(str(e))

    @command(permission='admin')
    def dump(self, mask, data, args):
        """Dump the state to a file.
            %%dump
        """
        self.save_history()

    @command(permission='admin')
    def index(self, mask, data, args):
        """Index markov models
            %%index [<n>] [<nick>]
        """
        n = args['<n>']
        if n is None:
            n = 2
        else:
            try:
                n = validate_n(n)
            except ValueError as e:
                sender = mask.split('!')[0]
                self.send_message(sender, str(e))
                return

        nick = args['<nick>']
        if nick:
            try:
                timed_messages = self.history[nick]
            except KeyError:
                self.send_message_to_admin('no history for nick {}'.format(nick))
            else:
                messages = history_messages(timed_messages)
                index_model_for_nick(nick, messages, n)
        else:
            self.index_all(n)

    @command(permission='imitate')
    @coroutine
    def imitate(self, mask, data, args):
        """Imitate another person, passing in the number of words to generate
        and the word to start with.
            %%imitate <nick>
        """
        nick = args['<nick>']

        # generate message
        try:
            message = yield from generate_imitation(nick)
        except NickNotIndexed as e:
            sender = mask.split('!')[0]
            self.send_message(sender, 'nick not indexed {}'.format(e.nick))
        except RuntimeError as e:
            self.send_message_to_admin(str(e))
            print(e, file=sys.stderr)
        else:
            self.send_message_to_channel('< {}> {}'.format(nick, message))

    @command(permission='view')
    def help(self, mask, data, args):
        """I'm not here to help!
            %%help [<command>]
        """
        yield '404 - Not Found'

    @cron('0 12,18 * * 1-5')
    def dump_task(self):
        self.save_history()

    @cron('0 09-18 * * 1-5')
    def index_task(self):
        self.index_all()

    def save_history(self):
        if self.history:
            filename = save_history(self.history)
            nb_nicks = len(self.history)
            nb_messages = sum(len(messages) for messages in self.history.values())
            self.send_message_to_admin('saved {} messages from {} nicks to {}'.format(
                nb_messages, nb_nicks, filename))

    def index_all(self, n=2):
        if self.history:
            index_models_for_history(self.history, n)

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask, data, target, **kwargs):
        if target == self.CHANNEL and not data.startswith('!') and not data.startswith('/'):
            nick = mask.split('!')[0]
            self.history.setdefault(nick, [])
            self.history[nick].append((time.time(), data))

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
