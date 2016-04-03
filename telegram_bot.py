import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
from telegram.ext import Updater

from base_bot import BaseBot

class TelegramBot(BaseBot):
    CHANNEL = 94361026
    ADMIN = '@jmcomets'

    def __init__(self, token):
        super().__init__(self.CHANNEL, self.ADMIN)
        self.updater = Updater(token=token)
        self._setup_commands()

    def _setup_commands(self):
        d = self.updater.dispatcher
        d.addTelegramMessageHandler(self.message_handler)
        d.addTelegramCommandHandler('imitate', self.imitate_command)
        d.addTelegramCommandHandler('index', self.index_command)
        d.addTelegramCommandHandler('load', self.load_command)
        d.addTelegramCommandHandler('save', self.save_command)

    def send_message(self, target, message):
        if self.bot is not None:
            logging.info('sending {} to {}'.format(message, target))
            self.bot.sendMessage(chat_id=target, text=message)

    def index_command(self, bot, update):
        self.bot = bot
        self.index_all()

    def load_command(self, bot, update):
        self.load_latest_history()

    def save_command(self, bot, update):
        self.save_history()

    def imitate_command(self, bot, update):
        self.bot = bot
        self.imitate_nick(update.message.chat_id,
                          '@{}'.format(update.message.from_user.username),
                          update.message.text.split()[1])

    def message_handler(self, bot, update):
        self.bot = bot
        self.on_message(update.message.chat_id,
                        update.message.from_user.username,
                        update.message.text)

    def run(self):
        self.updater.start_polling()

if __name__ == '__main__':
    bot = TelegramBot('218049029:AAHdVZmmvfxYZ1wzSNBDUiWCNmgCLXkiNh0')
    bot.run()
