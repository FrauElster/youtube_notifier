# pylint: disable=W1203
# pylint: disable=C0111


import logging
from typing import Dict, List

from future.backports.datetime import datetime
from telegram import Bot
from telegram import update
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater

from notifier.STRINGS import STRINGS
from notifier.filehandler import load_file, save_file
from notifier.youtube_crawler import YoutubeCrawler

LOGGER: logging.Logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        data: Dict[str, any] = self._load_data()
        secrets: Dict[str, str] = load_file(STRINGS.CONFIG_FILE)
        if "telegram_bot_token" not in secrets or not secrets["telegram_bot_token"]:
            LOGGER.error(f'{TelegramBot.__name__}: No token provided in {STRINGS.CONFIG_FILE}')
            raise Exception(f"No Token defined in {STRINGS.CONFIG_FILE}")

        self.token = secrets["telegram_bot_token"]
        updater: Updater = Updater(self.token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('add', self.add))
        dispatcher.add_handler(CommandHandler('rm', self.rm))
        dispatcher.add_handler(CommandHandler('check', self.check))
        dispatcher.add_handler(CommandHandler('help', self.help))
        dispatcher.add_handler(CommandHandler('list', self.list))
        dispatcher.add_handler(MessageHandler(Filters.command, self.unknown))

        updater.start_polling()
        LOGGER.info(f"{TelegramBot.__name__}: Started")

    def get_name(self, chat_id: int) -> str:
        """
        :param chat_id: the chat id
        :return: the full name of the user
        """
        bot: Bot = Bot(self.token)
        return f'{bot.getChat(chat_id=chat_id).first_name} {bot.getChat(chat_id=chat_id).last_name}'

    def get_username(self, chat_id: int) -> str:
        """
        :param chat_id: the chat id
        :return: the full username of the user
        """
        bot: Bot = Bot(self.token)
        return f'{bot.getChat(chat_id).username}'

    def get_all_user(self, telegram_data: Dict[str, any] = None) -> List[str]:
        """
        Returns a list with all users stored in the TELEGRAM_FILE
        :param telegram_data: if present it doesnt load it up again
        :return: a list with all users
        """
        if not telegram_data:
            telegram_data = self._load_data()
        if not telegram_data:
            return []

        return list(map(lambda chat_id: self.get_name(chat_id=chat_id), telegram_data.keys()))

    @classmethod
    def get_all_queries(cls, telegram_data: Dict[str, any] = None) -> List[str]:
        """
        Returns a list with all queries in the TELEGRAM_FILE, no double entries
        :param telegram_data: the telegram data if already loaded
        :return: a list containing all query strings
        """
        query_set: set = set()

        if not telegram_data:
            telegram_data = cls._load_data()
        if not telegram_data:
            return []

        map(lambda user: map(lambda query: query_set.add(query), list(map(lambda query_tuple: query_tuple[0],
                                                                          user["queries"]))), telegram_data)
        return list(query_set)

    @staticmethod
    def unknown(bot: Bot, telegram_update: update):
        """
        the method gets called when an unknown command is typed
        :param bot:
        :param telegram_update:
        :return:
        """
        chat_id = telegram_update.message.chat_id
        bot.send_message(chat_id=chat_id, text=STRINGS.TELEGRAM_UNKNOWN_COMMAND)

    @staticmethod
    def help(bot: Bot, telegram_update: update):
        """
        sends the user a list with all commands and explanations
        :param bot:
        :param telegram_update:
        :return:
        """
        chat_id = telegram_update.message.chat_id
        bot.send_message(chat_id=chat_id, text=STRINGS.TELEGRAM_HELP)

    @classmethod
    def start(cls, bot: Bot, telegram_update: update):
        """
        the welcome message of the bot
        :param bot:
        :param telegram_update:
        :return:
        """
        chat_id = telegram_update.message.chat_id
        bot.send_message(chat_id=chat_id, text=STRINGS.TELEGRAM_WELCOME)
        cls._save(telegram_data={}, chat_id=chat_id)
        LOGGER.info(f'{TelegramBot.__name__}: Welcome send')

    @classmethod
    def add(cls, bot: Bot, telegram_update: update):
        """
        adds query subscription of the user
        This method gets called by the user command "/add"
        :param bot:
        :param telegram_update:
        :return:
        """
        chat_id: int = telegram_update.message.chat_id
        username: str = telegram_update.message.from_user["username"]
        text: str = telegram_update.message.text[5:]
        if not text:
            LOGGER.info(f'{username} tried to add empty query')
            bot.send_message(chat_id=chat_id, text=STRINGS.TELEGRAM_EMPTY_QUERY)
            return

        telegram_data: Dict[str, any] = cls._load_data(chat_id)
        already_registered_queries: List[str] = list(map(lambda query_tuple: query_tuple[0], telegram_data["queries"]))

        queries: List[str] = text.split(", ") if ", " in text else [text]
        failed_queries: List[str] = []
        accepted_queries: List[str] = []
        for query in queries:
            if query in already_registered_queries:
                LOGGER.info(f'{username} tried to a already existing query "{query}"')
                failed_queries.append(query)
            else:
                accepted_queries.append(query)

        if failed_queries:
            bot.send_message(chat_id=chat_id,
                             text=f'{STRINGS.TELEGRAM_ALREADY_REG_QUERIES}{failed_queries}')
        if accepted_queries:
            bot.send_message(chat_id=chat_id, text=f'{STRINGS.TELEGRAM_QUERIES}{accepted_queries}')
            for new_query_string in accepted_queries:
                telegram_data["queries"].append([new_query_string, datetime(year=2010, month=1, day=1)])

        LOGGER.info(f'{username} added queries: {accepted_queries}\nFailed to add {failed_queries}')
        cls._save(telegram_data, chat_id)

    @classmethod
    def rm(cls, bot: Bot, telegram_update: update):
        """
        removes subscribed queries of the user
        This method gets called by the user command "/rm"
        :param bot:
        :param telegram_update:
        :return:
        """
        chat_id = telegram_update.message.chat_id
        username: str = telegram_update.message.from_user["username"]
        text: str = telegram_update.message.text[4:]
        if not text:
            LOGGER.info(f'{username} tried to remove empty query')
            bot.send_message(chat_id=chat_id, text=STRINGS.TELEGRAM_EMPTY_QUERY)
            return

        telegram_data: Dict[str, any] = cls._load_data(chat_id)
        already_registered_queries: List[str] = list(map(lambda query_tuple: query_tuple[0], telegram_data["queries"]))
        queries: List[str] = text.split(", ") if ", " in text else [text]
        refused_queries: List[str] = []
        accepted_queries: List[str] = []
        for query in queries:
            if query not in already_registered_queries:
                refused_queries.append(query)
            else:
                accepted_queries.append(query)

        map(lambda query: telegram_data["queries"].pop(query), accepted_queries)
        telegram_data["queries"] = list(filter(lambda query: query[0] not in accepted_queries, telegram_data["queries"]))

        if refused_queries:
            bot.send_message(chat_id=chat_id, text=f'{STRINGS.TELEGRAM_REFUSED_QUERIES}{refused_queries}')
        if accepted_queries:
            bot.send_message(chat_id=chat_id, text=f'{STRINGS.TELEGRAM_REMOVED_QUERIES}{accepted_queries}')

        LOGGER.info(f'{username} removed queries: {accepted_queries}\nFailed to remove {refused_queries}')

        cls._save(telegram_data, chat_id)

    @classmethod
    def check(cls, bot: Bot, telegram_update: update):
        """
        checks if any new videos matching the users subscriptions were uploaded
        This method gets called by the user command "/check"
        :param bot:
        :param telegram_update:
        :return:
        """
        chat_id = telegram_update.message.chat_id
        username: str = telegram_update.message.from_user["username"]
        new_videos: List[str] = cls._check(bot=bot, chat_id=chat_id, username=username)
        cls.notify(new_videos=new_videos, chat_id=chat_id, bot=bot)

    @classmethod
    def list(cls, bot: Bot, telegram_update: update):
        """
        Lists all subscriptions of the user
        This method gets called by the user command "/list"

        :param bot:
        :param telegram_update:
        :return:
        """
        chat_id = telegram_update.message.chat_id
        username: str = telegram_update.message.from_user["username"]
        telegram_data: Dict[str, any] = cls._load_data(chat_id)
        registered_queries: List[str] = list(map(lambda query: query[0], telegram_data["queries"]))

        bot.send_message(chat_id=chat_id, text=f'{STRINGS.TELEGRAM_LIST_MSG}{registered_queries}')

    @classmethod
    def notify(cls, new_videos: List[str], chat_id: int, bot: Bot):
        """
        Notifies the user of the new videos
        :param new_videos: a list of all new videos
        :param chat_id: the chat_id of the user to notifier
        :param bot: the bot
        :return:
        """
        telegram_data: Dict[str, any] = cls._load_data(chat_id)
        registered_queries: List[str] = list(map(lambda query_tuple: query_tuple[0], telegram_data["queries"]))
        msg: str = ""

        for new_video in new_videos:
            vid_query: str = new_video.split(": ")[0]
            if vid_query in registered_queries:
                msg = f'{msg}\n\n{new_video}'

        if msg:
            msg = f'{STRINGS.TELEGRAM_NOTIFICATION_MSG}\n\n{msg}'
        else:
            msg = STRINGS.TELEGRAM_NO_NEW_VIDEOS
        bot.send_message(chat_id=chat_id, text=msg)

    def check_all(self):
        """
        Iterates over all users and checks for new videos
        :return:
        """
        telegram_data: Dict[str, any] = self._load_data()
        bot: Bot = Bot(self.token)
        for chat_id in telegram_data.keys():
            username: str = self.get_username(chat_id)
            new_videos: List[str] = self._check(bot=bot, chat_id=chat_id, username=username)
            if new_videos:
                self.notify(new_videos=new_videos, chat_id=chat_id, bot=bot)

    @classmethod
    def _check(cls, bot: Bot, chat_id: int, username: str):
        telegram_data: Dict[str, any] = cls._load_data(chat_id=chat_id)
        crawler: YoutubeCrawler = YoutubeCrawler()
        results: List[str] = []
        queries: List[str] = telegram_data["queries"]

        for query in queries:
            search_term: str = query[0]
            last_checked: datetime = query[1]
            results.extend(crawler.search(search_term, last_check_datetime=last_checked))
            query[1] = datetime.now()

        LOGGER.info(f'{username} checks: new videos {results}')
        cls._save(telegram_data=telegram_data, chat_id=chat_id)
        return results

    @staticmethod
    def _load_data(chat_id: int = None) -> Dict[any, any]:
        """
        loads the telegram config
        :return:
        """
        config: Dict[str, any] = load_file(STRINGS.TELEGRAM_FILE)
        if not config:
            config = {}
        if "telegram_data" not in config.keys() or not config["telegram_data"]: # telegram data doesnt seem to be in keys
            LOGGER.warning(f'No "telegram_data" found in {STRINGS.TELEGRAM_FILE}')
            config["telegram_data"] = {}

        telegram_data: Dict[any, any] = config["telegram_data"]

        if not chat_id:
            return telegram_data

        if chat_id not in telegram_data.keys() or not telegram_data[chat_id] \
                or "queries" not in telegram_data[chat_id].keys() or not telegram_data[chat_id]["queries"]:
            telegram_data[chat_id] = {
                "queries": [],
            }

        return telegram_data[chat_id]

    @staticmethod
    def _save(telegram_data: Dict[str, any], chat_id: int = None):
        config: Dict[str, any] = load_file(STRINGS.TELEGRAM_FILE)
        if not config:
            config = {"telegram_data": {}}
        if chat_id:
            config["telegram_data"][chat_id] = telegram_data
        else:
            config["telegram_data"] = telegram_data

        save_file(file_name=STRINGS.TELEGRAM_FILE, data=config)
