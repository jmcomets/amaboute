import sys
from io import StringIO
import irc3
from irc3.plugins.command import command

@irc3.plugin
class Plugin:
    def __init__(self, bot):
        self.bot = bot
        self.ctx = dict()

    def send_message(self, message):
        self.bot.privmsg('#insa-if', message)

    @command(permission='eval')
    def eval(self, args, **kwargs):
        """Evaluate arbitrary Python code.
            %%eval [<code>...]
        """
        code = ' '.join(args['<code>'])
        if code:
            old_stdout, sys.stdout = sys.stdout, StringIO()
            try:
                exec(code, self.ctx)
            except SyntaxError as e:
                yield 'syntax error'
            except Exception as e:
                yield 'unknown exception: {}'.format(e)
            finally:
                captured_stdout, sys.stdout = sys.stdout.getvalue(), old_stdout
            for line in captured_stdout.split('\n'):
                yield line

    @command(permission='view')
    def help(self, **kwargs):
        """I'm not here to help!
            %%help [<command>]
        """
        yield 'STFU'
