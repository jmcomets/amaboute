import os
import json
import time
import irc3
from irc3.plugins.command import command
from history import load_latest_report, save_report
from quoting import matches_quote
from imitate import imitate_nick

this_dir = os.path.dirname(os.path.realpath(__file__))

@irc3.plugin
class Plugin:
    def __init__(self, bot):
        self.bot = bot
        self.quoters = {}
        self.history = {}

    def _get_report(self):
        return dict(quoters=self.quoters, history=self.history)

    def _set_report(self, report):
        self.quoters = report.get('quoters', {})
        self.history = report.get('history', {})

    report = property(_get_report, _set_report)

    def send_message(self, message):
        self.bot.privmsg('#insa-if', message)

    def send_message_to_admin(self, message):
        self.bot.privmsg('jmcomets', message)

    @command(permission='admin')
    def message(self, mask, data, args):
        """Send a message.
            %%message [<message>...]
        """
        self.send_message(' '.join(args['<message>']))

    @command(permission='admin')
    def load(self, mask, data, args):
        """Load the state from a file.
            %%load
        """
        self.report = load_latest_report()

    @command(permission='admin')
    def dump(self, mask, data, args):
        """Dump the state to a file.
            %%dump
        """
        save_report(self.report)

    @command(permission='admin')
    def reset(self, mask, data, args):
        """Reset the state.
            %%reset
        """
        self.history = {}
        self.quoters = {}

    @command(permission='report')
    def spammers(self, mask, data, args):
        """Report the spammers.
            %%spammers
        """
        if self.quoters:
            quoter, _ = max(self.quoters.items(), key=lambda i: i[1])
            self.send_message('Le top spammeur est {}'.format(quoter))

    @command(permission='imitate')
    def index(self, mask, data, args):
        """Index markov models
            %%index
        """
        if self.history:
            generate_models(self.history)

    @command(permission='imitate')
    def imitate(self, mask, data, args):
        """Imitate another person
            %%imitate <nick> [<amount>] [<start>]
        """
        nick = args['<nick>']
        start = args['<start>']
        try:
            amount = int(args['<amount>'])
        except (TypeError, ValueError):
            amount = 10

        try:
            message = imitate_nick(nick, amount, start)
        except (ValueError, RuntimeError) as e:
            self.send_message_to_admin(str(e))
        else:
            self.send_message('< {}> {}'.format(nick, message))

    @command(permission='view')
    def help(self, mask, data, args):
        """I'm not here to help!
            %%help [<command>]
        """
        yield '404 - Not Found'

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask, data, **kwargs):
        nick = mask.split('!')[0]
        if matches_quote(data):
            self.quoters.setdefault(nick, 0)
            self.quoters[nick] += 1
        self.history.setdefault(nick, [])
        self.history[nick].append((time.time(), data))
