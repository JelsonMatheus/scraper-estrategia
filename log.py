from pathlib import Path
from pytz import timezone
import logging
import datetime


TIMEZONE_SP = 'America/Sao_Paulo'


def get_logger():
    date_now = datetime.datetime.now()
    logger = logging.getLogger('scrappy')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    formatter.converter = lambda *args: datetime.datetime.now(tz=timezone(TIMEZONE_SP)).timetuple()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    path = Path(f"logs/")
    path.mkdir(parents=True, exist_ok=True)

    fileHandler = logging.FileHandler(path / f"{date_now.strftime('%d-%m-%Y %H:%M')}.log")
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger
