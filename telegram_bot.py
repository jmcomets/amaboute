import logging
from difflib import get_close_matches
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from slugify import slugify

logging.basicConfig(level=logging.DEBUG,
                    format=('%(asctime)s - '
                            '%(name)s - '
                            '%(levelname)s - '
                            '%(message)s'))

from models import add_message, get_registered_profiles, get_history
from imitate import Imitator

class TelegramBot:
    def __init__(self, token, admin, channel,
                 nb_messages_before_backup=100,
                 default_index_dimension=2):
        self.user_ids = {}
        self.admin = admin
        self.channel = channel
        self.updater = Updater(token=token)
        self.countdown = Countdown(nb_messages_before_backup)
        self.countdown.add_callback(self.on_countdown_finished)
        self.indexing_dimension = default_index_dimension
        self.setup_commands()
        self.imitation_models = ImitationModels()

    def setup_commands(self):
        self.updater.dispatcher.add_handler(MessageHandler([Filters.text], self.message_handler))
        self.add_command('imitate', aliases=['i'])
        self.add_command('dimension', aliases=['n'], admin_only=True)
        self.add_command('index', admin_only=True, fn=self.index_models, aliases=['r'])

    def get_username(self, user):
        username = user.username
        if not username:
            username = slugify('{} {}'.format(user.first_name, user.last_name))
        else:
            username = username.lower()
        return username

    def add_command(self, name, admin_only=False, fn=None, aliases=None):
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
            username = self.get_username(update.message.from_user)
            has_authorization = not admin_only or username == self.admin
            spamming = update.message.chat_id == self.channel
            if has_authorization and not spamming:
                fn(username, update.message.text)

        # add commands
        self.updater.dispatcher.add_handler(CommandHandler(name, inner))
        for alias in aliases:
            self.updater.dispatcher.add_handler(CommandHandler(alias, inner))

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

    def dimension_command(self, username, message):
        args = message.strip().split()
        if len(args) < 2:
            self.send_message_to_user(username, 'No N specified')
            return
        try:
            n = int(args[1])
        except ValueError:
            self.send_message_to_user(username, 'Could not convert {} to an integer'.format(args[1]))
        else:
            self.indexing_dimension = n
            self.index_models()

    def get_registered_nicknames(self):
        return set(map(lambda p: p.nickname,
                       get_registered_profiles()))

    def guess_username(self, username):
        username = username.lower()
        candidates = self.get_registered_nicknames()
        if username in candidates:
            return username
        matches = get_close_matches(username, candidates, 1)
        try:
            return matches[0]
        except IndexError:
            return None

    def imitate_command(self, username, message):
        candidates = self.get_registered_nicknames()
        args = message.strip().split()
        if len(args) < 2:
            self.send_message_to_user(username, 'You could at least tell me WHO you want to imitate!')
            return
        tried_username = ' '.join(args[1:])
        user_to_imitate = self.guess_username(tried_username)
        if user_to_imitate is None:
            user_list = '\n'.join(map(lambda k: '- {}'.format(k), candidates))
            self.send_message_to_user(username, "Either you're drunk, dumb or "
                                                "an asshole, but {} ain't in "
                                                "my book. Here's those I know "
                                                "so far:\n{}".format(tried_username,
                                                                     user_list))
            return
        self.imitate_nick(username, user_to_imitate)

    def imitate_nick(self, username, user_to_imitate):
        try:
            imitation = self.imitation_models.generate_imitation(user_to_imitate)
        except NoSuchNick:
            self.send_message_to_user(username, 'no such nickname {}'.format(user_to_imitate))
            return
        if imitation is None:
            self.send_message_to_user(username, 'could not generate an imitation')
            return
        self.send_message(('[{}]: {}'
                           '\n'
                           '(sent by: {})').format(username,
                                                   imitation,
                                                   user_to_imitate))

    def index_models(self):
        self.imitation_models.index(self.indexing_dimension)

    def on_message(self, username, message):
        add_message(username, message)

    def on_countdown_finished(self):
        self.index_models()

    def message_handler(self, bot, update):
        self.bot = bot
        user = update.message.from_user
        username = self.get_username(user)
        self.user_ids[username] = user.id
        message = update.message.text
        chat = update.message.chat_id
        logging.info('received a message from {} on {}: {}'.format(username, chat, message))
        self.on_message(username, message)
        self.countdown.tick()

    def run(self):
        self.updater.start_polling()

class Countdown:
    def __init__(self, initial):
        self.callbacks = []
        self.initial = initial
        self.current = initial

    def tick(self):
        self.current -= 1
        if self.current <= 0:
            self.current = initial
        for callback in self.callbacks:
            callback()

    def add_callback(self, callback):
        self.callbacks.append(callback)

class ImitationModels:
    def __init__(self):
        self.models = {}

    def index(self, n):
        for nickname, messages in get_history():
            self.models[nickname] = Imitator(messages, n)

    def generate_imitation(self, nickname):
        try:
            model = self.models[nickname]
        except KeyError:
            raise NoSuchNick
        else:
            return model.generate_sentence()

class NoSuchNick(ValueError):
    pass
