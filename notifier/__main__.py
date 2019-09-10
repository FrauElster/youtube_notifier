import logging
import time
from datetime import datetime
from typing import Dict

from notifier.STRINGS import STRINGS
from notifier.filehandler import to_file_path, load_file, save_file
from notifier.telegram_bot import TelegramBot
from notifier.utils import str_to_datetime

LOGGER: logging.Logger = logging.getLogger("notifier")


def main():
    setup_logger()
    bot: TelegramBot = TelegramBot()

    while True:
        bot.check_all()
        time.sleep(6*60*60)


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


def load_last_checked() -> datetime:
    config: Dict[str, any] = load_file(STRINGS.CONFIG_FILE)
    return str_to_datetime(config["last_checked"]) if "last_checked" in config.keys() else datetime(year=2010, month=1,
                                                                                                    day=1)


def _safe_last_checked(last_checked: datetime):
    config: Dict[str, any] = load_file(STRINGS.CONFIG_FILE)
    config["last_checked"] = str(last_checked)
    save_file(file_name=STRINGS.CONFIG_FILE, data=config)


if __name__ == '__main__':
    main()
