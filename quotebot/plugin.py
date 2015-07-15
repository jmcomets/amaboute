import irc3
from irc3.plugins.command import command
import pipeau
import quotes

@irc3.plugin
class Plugin:
    def __init__(self, bot):
        self.bot = bot

    @command(permission='view')
    def eddy_malou(self, mask, target, args):
        """Quotes from http://eddy-malou.com.

            %%eddy_malou
        """
        yield pipeau.eddy_malou()

    @command(permission='view')
    def pipotronic(self, mask, target, args):
        """Quotes from http://www.pipotronic.com.

            %%pipotronic
        """
        yield pipeau.pipotronic()

    @command(permission='view')
    def quote(self, mask, target, args):
        """Quotes from http://cubemonkey.net/quotes.

            %%quote <topic>
        """
        topic = args['<topic>']
        if topic not in quotes.available_topics:
            yield 'Invalid topic'
        else:
            yield quotes.quote_topic(topic)

    @command(permission='view')
    def topics(self, mask, target, args):
        """List topics from http://cubemonkey.net/quotes.

            %%topics
        """
        yield 'Available topics: %s' % ', '.join(quotes.available_topics)
