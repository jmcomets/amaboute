import time
import irc3
from irc3.plugins.command import command

@irc3.plugin
class Plugin:
    def __init__(self, bot):
        self.bot = bot
        self.targeters = set()
        self.targeted_users = set()
        self.times = dict()

    def send_message(self, message):
        self.bot.privmsg('#insa-if', message)

    # manage targeters

    @command(permission='manage')
    def allow_targeting(self, mask, data, args):
        """Allow a user to target others.
            %%allow_targeting <targeter>
        """
        nick = mask.split('!')[0]
        targeter = args['<targeter>']
        self.targeters.add(targeter)

    @command(permission='manage')
    def disallow_targeting(self, mask, data, args):
        """Disallow a user to target others.
            %%disallow_targeting <targeter>
        """
        targeter = args['<targeter>']
        self.targeters.remove(targeter)

    @command(permission='view')
    def list_targeters(self, mask, data, args):
        """List the targeters
            %%list_targeters
        """
        yield 'targeters: {}'.format(', '.join(self.targeters) or 'none')

    # manage targeted users

    @command(permission='target')
    def add_targeted_user(self, mask, data, args):
        """Add a targeted user.
            %%add_targeted_user <targeted>
        """
        targeted = args['<targeted>']
        self.targeted_users.add(targeted)

    @command(permission='target')
    def remove_targeted_user(self, mask, data, args):
        """Remove a targeted user.
            %%remove_targeted_user <targeted>
        """
        targeted = args['<targeted>']
        self.targeted_users.remove(targeted)

    @command(permission='view')
    def list_targeted(self, mask, data, args):
        """List the targeted users.
            %%list_targeted
        """
        yield 'targeted users: {}'.format(', '.join(self.targeted_users) or 'none')

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask, data, **kwargs):
        nick = mask.split('!')[0]
        if nick in self.targeted_users:
            t = time.time()
            if nick not in self.times or abs(self.times[nick] - t) > 10:
                self.send_message('Ta gueule {} !'.format(nick))
                self.times[nick] = t

    @irc3.event(irc3.rfc.NEW_NICK)
    def on_new_nick(self, nick, new_nick, **kwargs):
        nick = nick.split('!')[0]
        if nick in self.targeted_users:
            self.targeted_users.remove(nick)
            self.targeted_users.add(new_nick)
            if nick in self.times:
                self.times[new_nick] = self.times[nick]
