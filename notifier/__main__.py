import logging
from datetime import datetime
from typing import List, Dict

from notifier.STRINGS import STRINGS
from notifier.filehandler import to_file_path, load_file, save_file
from notifier.telegram_bot import TelegramBot
from notifier.youtube_crawler import YoutubeCrawler, Video

LOGGER: logging.Logger = logging.getLogger("notifier")


def main():
    setup_logger()
    bot: TelegramBot = TelegramBot()
    # run()

def run():
    config: Dict[str, any] = load_config()
    crawler: YoutubeCrawler = YoutubeCrawler()
    results: List[Video] = []

    for querry in config["querries"]:
        # results = results + crawler.search(querry, datetime.strptime(config["last_checked"].split(".")[0], '%Y-%m-%d %H:%M:%S'))
        results = results + crawler.search(querry, datetime.strptime('2019-01-01 20:21:11', '%Y-%m-%d %H:%M:%S'))

    config["last_checked"] = str(datetime.now())
    save_file(file_name=STRINGS.CONFIG_FILE, data=config)

    results_serialize: List[str] = list(map(lambda video: video.serialize(), results))

    telegrambot: TelegramBot = TelegramBot()
    telegrambot.notify_youtube_update(results)
    save_file(file_name=STRINGS.OUTPUT_FILE, data=results_serialize)


def setup_logger() -> None:
    """
    setup for the various handler for logging
    :return:
    """
    LOGGER.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s \t|%(asctime)s \t| %(name)s \t|  %(message)s')

    # DEBUG change mode to append for production
    file_handler: logging.FileHandler = logging.FileHandler(to_file_path(STRINGS.LOG_FILENAME), mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler: logging.StreamHandler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(console_handler)
    LOGGER.info('Filehandler and Console_Handler were born, let\'s start logging')


def load_config() -> Dict[str, any]:
    config: Dict[str, any] = load_file(STRINGS.CONFIG_FILE)
    if "querries" not in config.keys() or not config["querries"]:
        LOGGER.warning(f"No querries in {STRINGS.CONFIG_FILE}")
        exit(0)
    if "last_checked" not in config.keys() or not config["last_checked"]:
        config["last_checked"] = datetime(year=2010, month=1, day=1)
        LOGGER.warning(f'No "last_checked" in {STRINGS.CONFIG_FILE}, set to {config["last_checked"]}')

    return config

if __name__ == '__main__':
    main()
