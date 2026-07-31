import logging
from colorama import Fore, Style

# Добавляем кастомный уровень глобально
DEBUG_LOG_LEVEL = 15
DB_LEVEL = 32
BOT_LEVEL = 35
logging.addLevelName(DEBUG_LOG_LEVEL, "DEBUG_LOG")
logging.addLevelName(DB_LEVEL, "DB")
logging.addLevelName(BOT_LEVEL, "BOT")


def debug_log(self, message, *args, **kwargs):
    if self.isEnabledFor(DEBUG_LOG_LEVEL):
        self._log(DEBUG_LOG_LEVEL, message, args, **kwargs)


def db(self, message, *args, **kwargs):
    if self.isEnabledFor(DB_LEVEL):
        self._log(DB_LEVEL, message, args, **kwargs)


def bot(self, message, *args, **kwargs):
    if self.isEnabledFor(BOT_LEVEL):
        self._log(BOT_LEVEL, message, args, **kwargs)


logging.Logger.debug_log = debug_log
logging.Logger.db = db
logging.Logger.bot = bot


class RainbowLogger:
    class ColoramaFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': Fore.GREEN,  # 10
            'DEBUG_LOG': Fore.YELLOW,
            'INFO': Fore.LIGHTGREEN_EX,  # 20

            'DB': Fore.LIGHTYELLOW_EX,
            'BOT': Fore.LIGHTBLUE_EX,

            'WARNING': Fore.LIGHTYELLOW_EX,  # 30
            'ERROR': Fore.LIGHTRED_EX,  # 40
            'CRITICAL': Fore.LIGHTMAGENTA_EX,  # 50
        }

        def format(self, record):
            color = self.COLORS.get(record.levelname, '')
            if record.levelname == 'BOT' or record.levelname == 'DEBUG_LOG':
                log_format = '%(asctime)s - %(message)s'
            else:
                log_format = '%(asctime)s - %(levelname)s – %(funcName)s - %(message)s'
            log_fmt = f"{color}{log_format}{Style.RESET_ALL}"
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)

    def __init__(self, log_level=logging.WARNING):
        logging.basicConfig(
            level=log_level,
            datefmt='%Y-%m-%d %H:%M:%S',
            encoding='utf-8'
        )
        logging.getLogger().handlers[0].setFormatter(self.ColoramaFormatter())


def run_rainbow(level=logging.DEBUG):
    RainbowLogger(level)
    logger = logging.getLogger(__name__)
    return logger


if __name__ == '__main__':
    logger = run_rainbow(logging.DEBUG)

    logger.debug("debug message")
    logger.debug_log("log debug")
    logger.db("success message!")
    logger.bot("success message!")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")

    print("Test regular text")
