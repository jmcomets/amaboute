import logging
from difflib import get_close_matches
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
from telegram.ext import Updater
from slugify import slugify

from base_bot import BaseBot
from imitate import ALL_NICKS

class TelegramBot(BaseBot):
    def __init__(self, token, admin, channel, nb_messages_before_backup=100, default_index_dimension=2):
        super().__init__()
        self.admin = admin
        self.channel = channel
        self.updater = Updater(token=token)
        self.initial_countdown = nb_messages_before_backup
        self.countdown = self.initial_countdown
        self.user_ids = {}
        self.n = default_index_dimension
        self._setup_commands()

    def _setup_commands(self):
        self.updater.dispatcher.addTelegramMessageHandler(self.message_handler)
        self._add_command('imitate', aliases=['i'])
        self._add_command('dimension', aliases=['n'], admin_only=True)
        self._add_command('load', admin_only=True, fn=self.load_and_index, aliases=['l'])
        self._add_command('index', admin_only=True, fn=self.index_models, aliases=['r'])
        self._add_command('save', admin_only=True, fn=self.save_history, aliases=['s', 'w'])

    def _get_username(self, user):
        username = user.username
        if not username:
            username = slugify('{} {}'.format(user.first_name, user.last_name))
        else:
            username = username.lower()
        return username

    def _add_command(self, name, admin_only=False, fn=None, aliases=None):
        if aliases is None:
            aliases = []
        logging.info('adding command: {}, aliases are {}'.format(name, ', '.join(aliases)))

        # deduce command from methods
        if fn is None:
            try:
                fn = getattr(self, '{}_command'.format(name))
            except AttributeError:
                raise NotImplementedError('command {} not implemented'.format(name))
        else:
            old_fn, fn = fn, lambda _1, _2: old_fn()

        # decorator
        def inner(bot, update):
            logging.info('processing command {}'.format(name))
            self.bot = bot
            username = self._get_username(update.message.from_user)
            has_authorization = not admin_only or username == self.admin
            spamming = update.message.chat_id == self.channel
            if has_authorization and not spamming:
                fn(username, update.message.text)

        # add commands
        self.updater.dispatcher.addTelegramCommandHandler(name, inner)
        for alias in aliases:
            self.updater.dispatcher.addTelegramCommandHandler(alias, inner)

    def send_message(self, target, message):
        if self.bot is not None:
            logging.info('sending {} to {}'.format(message, target))
            self.bot.sendMessage(chat_id=target, text=message)

    def send_message_to_user(self, username, message):
        try:
            user_id = self.user_ids[username]
        except KeyError:
            logging.error('could not send message to {}: no associated user ID'.format(username))
        else:
            self.send_message(user_id, message)

    def _guess_username(self, username):
        username = username.lower()
        if username in self.history or username == ALL_NICKS:
            return username
        candidates = self.history.keys()
        matches = get_close_matches(username, candidates, 1)
        try:
            return matches[0]
        except IndexError:
            return None

    def imitate_command(self, username, message):
        if not self.history:
            self.send_message_to_user(username, "I'm sorry {}, I can't do that.".format(username))
            return
        args = message.strip().split()
        if len(args) < 2:
            self.send_message_to_user(username, 'You could at least tell me WHO you want to imitate!')
            return
        tried_username = ' '.join(args[1:])
        user_to_imitate = self._guess_username(tried_username)
        if user_to_imitate is None:
            user_list = '\n'.join(map(lambda k: '- {}'.format(k), self.history))
            self.send_message_to_user(username, "Either you're drunk, dumb or "
                                                "an asshole, but {} ain't in "
                                                "my book. Here's those I know "
                                                "so far:\n{}".format(tried_username,
                                                                     user_list))
            return
        self.imitate_nick(self.channel, username, user_to_imitate)

    def dimension_command(self, username, message):
        self.n = message
        args = message.strip().split()
        if len(args) < 2:
            self.send_message_to_user(username, 'No N specified')
            return
        try:
            n = int(args[1])
        except ValueError:
            self.send_message_to_user(username, 'Could not convert {} to an integer'.format(args[1]))
        else:
            self.n = n
            self.index_models()

    def index_models(self):
        self.index_all(self.n)

    def _post_message(self):
        self.countdown -= 1
        if self.countdown <= 0:
            self.save_history()
            self.index_models()
            self.countdown = self.initial_countdown

    def message_handler(self, bot, update):
        self.bot = bot
        user = update.message.from_user
        username = self._get_username(user)
        self.user_ids[username] = user.id
        message = update.message.text
        chat = update.message.chat_id
        logging.info('received a message from {} on {}: {}'.format(username, chat, message))
        self.on_message(username, message)
        self._post_message()

    def run(self):
        self.updater.start_polling()
