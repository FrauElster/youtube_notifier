# pylint: disable=W1203
# pylint: disable=C0111


import logging
from typing import Dict, List

from future.backports.datetime import datetime
from telegram import Bot
from telegram import update
from telegram.ext import CommandHandler
from telegram.ext import Updater

from notifier.STRINGS import STRINGS
from notifier.filehandler import load_file, save_file

LOGGER: logging.Logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        data: Dict[str, any] = self._load_data()
        secrets: Dict[str, str] = load_file(STRINGS.SECRETS_FILE)
        if "telegram_bot_token" not in secrets or not secrets["telegram_bot_token"]:
            LOGGER.error(f'{TelegramBot.__name__}: No token provided in {STRINGS.SECRETS_FILE}')
            raise Exception(f"No Token defined in {STRINGS.SECRETS_FILE}")
        updater: Updater = Updater(secrets["telegram_bot_token"])
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('add', self.add))
        dispatcher.add_handler(CommandHandler('rm', self.rm))
        dispatcher.add_handler(CommandHandler('check', self.check))
        updater.start_polling()
        LOGGER.info(f"{TelegramBot.__name__}: Started")

    @staticmethod
    def start(bot: Bot, telegram_update: update):
        """
        the welcome message of the bot
        :param bot:
        :param telegram_update:
        :return:
        """
        chat_id = telegram_update.message.chat_id
        bot.send_message(chat_id=chat_id, text=STRINGS.TELEGRAM_WELCOME)
        print(str(telegram_update.message.text))
        LOGGER.info(f'{TelegramBot.__name__}: Welcome send')

    @classmethod
    def add(cls, bot: Bot, telegram_update: update):
        chat_id: int = telegram_update.message.chat_id
        username: str = telegram_update.message.from_user["username"]
        text: str = telegram_update.message.text[5:]
        if not text:
            LOGGER.info(f'{username} tried to add empty query')
            bot.send_message(chat_id=chat_id, text=STRINGS.TELEGRAM_EMPTY_QUERY)
            return

        telegram_data: Dict[str, any] = cls._load_data()
        if cls._check_for_queries(telegram_data=telegram_data, username=username):
            telegram_data[username] = {
                "queries": [],
                "last_checked": datetime(year=2010, month=1, day=1)
            }
        already_registered_queries: List[str] = telegram_data[username]["queries"]

        queries: List[str] = text.split(", ") if ", " in text else [text]
        failed_queries: List[str] = []
        for query in queries:
            if query in already_registered_queries:
                LOGGER.info(f'{username} tried to a already existing query "{query}"}')
                failed_queries.append(query)
            else:
                already_registered_queries.append(query)

        if failed_queries:
            bot.send_message(chat_id=chat_id,
                             text=f'{STRINGS.TELEGRAM_ALREADY_REG_QUERIES}{failed_queries}')

        bot.send_message(chat_id=chat_id, text=f'{STRINGS.TELEGRAM_QUERIES}{already_registered_queries}')
        telegram_data[username]["queries"] = already_registered_queries
        cls._save(telegram_data)


    @classmethod
    def rm(cls, bot: Bot, telegram_update: update):
        chat_id = telegram_update.message.chat_id
        username: str = telegram_update.message.from_user["username"]
        text: str = telegram_update.message.text[5:]
        if not text:
            LOGGER.info(f'{username} tried to add empty querry')
            bot.send_message(chat_id=chat_id, text=STRINGS.TELEGRAM_EMPTY_QUERY)
            return
        telegram_data: Dict[str, any] = cls._load_data()
        if cls._check_for_queries(telegram_data=telegram_data, username=username):
            telegram_data[username] = {
                "queries": [],
                "last_checked": datetime(year=2010, month=1, day=1)
            }
        registered_queries: List[str] = telegram_data[username]["queries"]
        #todo   
        queries: List[str] = text.split(", ") if ", " in text else [text]
        refused_queries: List[str] = []
        accepted_queries: List[str] = []
        if username in telegram_data and telegram_data[username]:
            for query in queries:
                if query not in telegram_data[username]:
                    refused_queries.append(query)
                else:
                    accepted_queries.append(query)
        else:
            refused_queries = queries
        if refused_queries:
            bot.send_message(chat_id=chat_id, text=f'{STRINGS.TELEGRAM_REFUSED_QUERIES}{refused_queries}')

        for accepted_query in accepted_queries:
            telegram_data[username].pop(accepted_query)
        if accepted_queries:
            bot.send_message(chat_id=chat_id, text=f'{STRINGS.TELEGRAM_REMOVED_QUERIES}{accepted_queries}')

        cls._save(telegram_data)


    @classmethod
    def check(cls, bot: Bot, telegram_update: update):
        pass


    def notify(self, msg: str):
        """
        notifies all subscribed user
        :return:
        """
        bot: Bot = Bot(self.token)
        telegram_data: Dict[str, any] = self._load_data()
        if not telegram_data["chat_ids"]:
            LOGGER.warning(f'Telegram Bot: No chat_ids to notify')
            return

        names: List[str] = list(map(lambda chat_id: self.get_name(chat_id), telegram_data["chat_ids"]))

        LOGGER.info(f'Telegram Bot: send notifications to "{names}"')
        for chat_id in telegram_data["chat_ids"]:
            bot.send_message(chat_id=chat_id, text=msg)
            logfile = to_file_path(STRINGS.LOG_FILENAME)
            bot.send_document(chat_id=chat_id, document=open(logfile, 'rb'), filename="Logfile")


    @staticmethod
    def _load_data() -> Dict[str, any]:
        """
        loads the telegram config
        :return:
        """
        config: Dict[str, any] = load_file(STRINGS.CONFIG_FILE)
        if "telegram_data " not in config or config["telegram_data"]:
            LOGGER.warning(f'No "telegram_data" found in {STRINGS.CONFIG_FILE}')
            config["telegram_data"] = {}

        return config["telegram_data"]


    @staticmethod
    def _save(telegram_data: Dict[str, any]):
        config: Dict[str, any] = load_file(STRINGS.CONFIG_FILE)
        config["telegram_data"] = telegram_data
        save_file(file_name=STRINGS.CONFIG_FILE, data=config)


    @staticmethod
    def _check_for_queries(telegram_data: Dict[str, any], username: str) -> bool:
        return username not in telegram_data.keys() or not telegram_data[username] \
                or "queries" not in telegram_data[username].keys() or not telegram_data[username]["queries"]

    @staticmethod
    def get_name(chat_id: int) -> str:
        """
        :param chat_id: the chat id
        :return: the full name of the user
        """
        return f'{Bot.getChat(chat_id).first_name} {Bot.getChat(chat_id).last_name}'


    @staticmethod
    def get_username(chat_id: int) -> str:
        """
        :param chat_id: the chat id
        :return: the full username of the user
        """
        return f'{Bot.getChat(chat_id).username}'
