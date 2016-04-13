import logging
from difflib import get_close_matches
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
from telegram.ext import Updater

from base_bot import BaseBot

class TelegramBot(BaseBot):
    def __init__(self, token, admin, channel, nb_messages_before_backup=100):
        super().__init__()
        self.admin = admin
        self.channel = channel
        self.updater = Updater(token=token)
        self.initial_countdown = nb_messages_before_backup
        self.countdown = self.initial_countdown
        self._setup_commands()

    def _setup_commands(self):
        self.updater.dispatcher.addTelegramMessageHandler(self.message_handler)
        self._add_command('imitate')
        self._add_command('load', admin_only=True, fn=self.load_latest_history)
        self._add_command('index', admin_only=True, fn=self.index_all)
        self._add_command('save', admin_only=True, fn=self.save_history)

    def _add_command(self, name, admin_only=False, fn=None):
        if fn is None:
            try:
                fn = getattr(self, '{}_command'.format(name))
            except AttributeError:
                raise NotImplementedError('command {} not implemented'.format(name))
        else:
            old_fn, fn = fn, lambda _1, _2: old_fn()
        def inner(bot, update):
            self.bot = bot
            username = update.message.from_user.username
            has_authorizaion = not admin_only or username == self.admin
            spamming = update.message.chat_id == self.channel
            if has_authorizaion and not spamming:
                fn(username, update.message.text)
        self.updater.dispatcher.addTelegramCommandHandler(name, inner)

    def send_message(self, target, message):
        if self.bot is not None:
            logging.info('sending {} to {}'.format(message, target))
            self.bot.sendMessage(chat_id=target, text=message)

    def _guess_username(self, username):
        candidates = self.history.keys()
        matches = get_close_matches(username, candidates, 1)
        try:
            return matches[0]
        except IndexError:
            return None

    def imitate_command(self, username, message):
        if not self.history:
            return
        args = message.strip().split()
        if len(args) < 2:
            return
        user_to_imitate = self._guess_username(' '.join(args[1:]))
        if user_to_imitate is not None:
            self.imitate_nick(self.channel, username, user_to_imitate)

    def _post_message(self):
        self.countdown -= 1
        if self.countdown <= 0:
            self.save_history()
            self.index_all()
            self.countdown = self.initial_countdown

    def message_handler(self, bot, update):
        self.bot = bot
        username = update.message.from_user.username
        message = update.message.text
        chat = update.message.chat_id
        logging.info('received a message from {} on {}: {}'.format(username, chat, message))
        self.on_message(username, message)
        self._post_message()

    def run(self):
        self.updater.start_polling()
