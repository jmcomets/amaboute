import irc3
from irc3.plugins.command import command

@irc3.plugin
class Plugin:
    def __init__(self, bot):
        self.bot = bot

    def send_message(self, message):
        self.bot.privmsg('#insa-if', message)

    @irc3.event(irc3.rfc.PRIVMSG)
    def on_privmsg(self, mask, data, **kwargs):
        nick = mask.split('!')[0]
        data = ''.join(filter(lambda c: c not in '.;,?!', data.lower())).split()
        if 'bépo' in data or 'bepo' in data:
            self.send_message("{}: le bépo c'est nul".format(nick))

    @command(permission='view')
    def help(self, **kwargs):
        """I'm not here to help!
            %%help [<command>]
        """
        yield 'STFU'
