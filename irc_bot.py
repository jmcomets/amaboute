import irc3
from irc3.plugins.command import command
from irc3.plugins.cron import cron

from base_bot import BaseBot

@irc3.plugin
class IrcBot(BaseBot):
    CHANNEL = '#insa-if'

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.history = {}

    def send_message(self, target, message):
        self.bot.privmsg(target, message)

    @command(permission='admin')
    def message(self, mask, target, args):
        """Send a message.
            %%message [<message>...]
        """
        self.send_message(self.CHANNEL, ' '.join(args['<message>']))

    @command(permission='admin')
    def load(self, mask, target, args):
        """Load the state from a file.
            %%load
        """
        self.load_latest_history()

    @command(permission='admin')
    def dump(self, mask, target, args):
        """Dump the state to a file.
            %%dump
        """
        self.save_history()

    @command(permission='admin')
    def index(self, mask, target, args):
        """Index markov models
            %%index [<n>] [<nick>]
        """
        n = args['<n>']
        nick = args['<nick>']
        sender = mask.split('!')[0]
        self.index_models(sender, nick, n)

    @command(permission='imitate')
    def imitate(self, mask, target, args):
        """Imitate another person, passing in the number of words to generate
        and the word to start with.
            %%imitate <nick>
        """
        nick = args['<nick>']
        sender = mask.split('!')[0]
        self.imitate_nick(target, sender, nick)

    @command(permission='view')
    def help(self, mask, target, args):
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

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask, data, target, **kwargs):
        nick = mask.split('!')[0]
        self.on_message(nick, data)

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
