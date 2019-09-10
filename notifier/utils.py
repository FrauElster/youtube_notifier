from datetime import datetime


def str_to_datetime(date_str: str) -> datetime:
    """
    '2019-01-01 20:21:11' -> datetime object
    :param date_str:
    :return:
    """
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')