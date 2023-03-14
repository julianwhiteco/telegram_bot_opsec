import telebot
import sys
import pandas as pd
import re
from argparse import ArgumentParser
from time import time
from subprocess import check_output
from io import StringIO
from typing import Any

# Getting the API key provided in the docker run command.
parser = ArgumentParser()
parser.add_argument('-a', '--api_key', help='API Key passed at runtime')
args = parser.parse_args()
bot = telebot.TeleBot(str(args.api_key))

# Change this to limit how long someone must wait between lookups, or set it to 0 to disable rate limiting.
# Use this to reduce your compute bill if it's an issue.
rate_limit_seconds = 5

if args.api_key:
    print(f'API key provided. Running.')
else:
    print(f'A Telegram bot API key was not provided. Please run with "docker run image-name -a yourapikeyhere". If you do not have an API key, you can create a bot using @BotFather on Telegram. This application will now exit.')
    exit(1)


# Rate limiting function.
def rate_limit(user_id, rate_limit_seconds, warning_message):
    def decorator(func):
        def wrapper(message):
            if user_id in wrapper.last_command_times:  # todo: Need to flush this daily somehow.
                # Calculating time lapsed since user's last command:
                time_since_last_command = time() - wrapper.last_command_times[user_id]
                if time_since_last_command < rate_limit_seconds:
                    bot.send_message(chat_id=message.chat.id, text=warning_message)
                    return
            wrapper.last_command_times[user_id] = time()
            func(message)
        if not hasattr(wrapper, "last_command_times"):
            wrapper.last_command_times = {}
        return wrapper
    return decorator


@bot.message_handler(commands=['start', 'info'])
@rate_limit(lambda message: message.from_user.id, rate_limit_seconds, f"Rate limiting is currently set to one search every {rate_limit_seconds} seconds. Try again shortly.")
def send_welcome(message: Any) -> None:
    welcome = f"Use this bot with /whois username, and rate limiting is currently set to one search every {rate_limit_seconds} seconds.\n\nKeep in mind, that this bot only looks up the username provided, it does not cross-check usernames with other details, and some responses may be false positives. \n\nBuilt by @AshenTiger and utilises the WhatsMyName project: https://twitter.com/whatsmynameproj"
    bot.reply_to(message, welcome)


@bot.message_handler(commands=['whois'])
@rate_limit(lambda message: message.from_user.id, rate_limit_seconds, f"Rate limiting is currently set to one search every {rate_limit_seconds} seconds. Try again shortly.")
def whois(message: Any) -> None:
    whois_username = message.text.replace("/whois ", "")
    if whois_username.startswith("@"):
        whois_username = whois_username.removeprefix("@")
    bot.reply_to(message, f"Please wait while I look up: {whois_username}")

    try:
        pd.options.display.max_colwidth = 100  # Override of df length
        cmd = str(check_output([f"python3", "WhatsMyName/whats_my_name.py", "-u", whois_username]).decode(sys.stdout.encoding))
        df = pd.read_csv(StringIO(re.sub(r'[-+|]', '', cmd)), sep='\s{2,}', engine='python')
        df = df[['Site Name', 'Url']]
        df = df.to_string(index=False, header=False)
        df = re.sub(' +', ' ', df)
        df = re.sub(' ', '', df)
        df = re.sub('http', ': http', df)

        if "EmptyDataFrame" in df:
            bot.reply_to(message, f"I wasn't able to find any accounts with that username. Try another variation including adding or removing '-', '_' etc., or try another username.")
        else:
            bot.reply_to(message, str(df))

        print("DEBUG: Processed lookup dataset transmitted.")

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, f"An error occurred while running your search. Please try again, or notify an operator.")


bot.infinity_polling()
