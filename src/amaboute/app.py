import os
from amaboute.telegram_bot import TelegramBot

def with_env(f):
    @wraps(f)
    def inner(*args, **kwargs):
        env = {}

        prefix = 'AMABOUTE_'

        # read env file
        with open('.env', 'r') as fp:
            for line in fp.readlines():
                line = line.rstrip('\n')
                columns = line.split('=')
                if len(columns) < 2:
                    continue # TODO: log
                key, value = columns[0], '='.join(columns[1:])
                env[prefix % key.upper()] = value

        # overwrite with entries from os.environ
        for key, value in os.environ.items():
            if key.startswith(prefix):
                env[key] = value

        return f(env, *args, **kwargs)
    return inner

@with_env
def main(env):
    bot = TelegramBot(env['AMABOUTE_TOKEN'],
                      env['AMABOUTE_ADMIN'],
                      env['AMABOUTE_CHANNEL'])
    bot.run()

if __name__ == '__main__':
    main()
