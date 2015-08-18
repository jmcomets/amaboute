import time
import irc3
from irc3.plugins.command import command
from irc3.plugins.cron import cron
from history import load_latest_history, save_history
from imitate import imitate, generate_models_for_history, generate_model
from dictionaries import load_datasets
from recap import recap

@irc3.plugin
class Plugin:
    ADMIN = 'jmcomets'
    CHANNEL = 'insa-if'

    def __init__(self, bot):
        self.bot = bot
        self.history = {}

    def send_message(self, target, message):
        self.bot.privmsg(target, message)

    def send_message_to_channel(self, message):
        self.send_message('#{}'.format(self.CHANNEL), message)

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
        save_history(self.history)

    @command(permission='admin')
    def index(self, mask, data, args):
        """Index markov models
            %%index <n> [<nick>]
        """
        try:
            n = int(args['<n>'])
        except ValueError as e:
            self.send_message_to_admin(str(e))
        else:
            nick = args['<nick>']
            if nick:
                try:
                    timed_messages = self.history[nick]
                except KeyError:
                    self.send_message_to_admin('no history for nick {}'.format(nick))
                else:
                    messages = history_messages(messages)
                    generate_models_for_nick(nick, messages, n)
            else:
                if self.history:
                    generate_models_for_history(self.history, n)
                for nick, dataset in load_datasets():
                    generate_model(nick, dataset, n)

    @command(permission='imitate')
    def imitate(self, mask, data, args):
        """Imitate another person, passing in the number of words to generate
        and the word to start with.
            %%imitate <nick> [<amount>] [<start>]
        """
        nick = args['<nick>']
        start = args['<start>']
        try:
            amount = int(args['<amount>'])
        except (TypeError, ValueError):
            amount = 10

        # generate message
        try:
            message = imitate(nick, amount, start)
        except (KeyError, ValueError, RuntimeError) as e:
            self.send_message_to_admin(str(e))
        else:
            self.send_message_to_channel('< {}> {}'.format(nick, message))

    @command(permission='recap')
    def recap(self, mask, data, args):
        """Recap of the day.
            %%recap
        """
        self.send_recap()

    @command(permission='view')
    def help(self, mask, data, args):
        """I'm not here to help!
            %%help [<command>]
        """
        yield '404 - Not Found'

    @cron('* 17 * * *')
    def recap_task(self):
        self.send_recap()

    def send_recap(self):
        if self.history:
            recap_so_far = recap(self.history)
            messages = """Récapitulatif :
            - activité : {most_active}
            - hashtags : {most_hashtags}
            - partages : {most_shares}""".format(**recap_so_far).split('\n')
            for message in messages:
                self.send_message_to_channel(message)

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask, data, target, **kwargs):
        if target == self.CHANNEL and not data.startswith('!') and not data.startswith('/'):
            nick = mask.split('!')[0]
            self.history.setdefault(nick, [])
            self.history[nick].append((time.time(), data))
