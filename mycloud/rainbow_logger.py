import logging

from colorama import Fore, Style

DEBUG_LOG_LEVEL = 15
DB_LEVEL = 32
BOT_LEVEL = 35

logging.addLevelName(DEBUG_LOG_LEVEL, "DEBUG_LOG")
logging.addLevelName(DB_LEVEL, "DB")
logging.addLevelName(BOT_LEVEL, "BOT")


class ColoramaFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Fore.GREEN,
        "DEBUG_LOG": Fore.YELLOW,
        "INFO": Fore.LIGHTGREEN_EX,
        "DB": Fore.LIGHTYELLOW_EX,
        "BOT": Fore.LIGHTBLUE_EX,
        "WARNING": Fore.LIGHTYELLOW_EX,
        "ERROR": Fore.LIGHTRED_EX,
        "CRITICAL": Fore.LIGHTMAGENTA_EX,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        if record.levelname in ("BOT", "DEBUG_LOG"):
            log_format = "%(asctime)s - %(message)s"
        else:
            log_format = "%(asctime)s - %(levelname)s – %(funcName)s - %(message)s"
        log_fmt = f"{color}{log_format}{Style.RESET_ALL}"
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class RainbowLogger(logging.LoggerAdapter):
    def debug_log(self, message, *args, **kwargs) -> None:
        if self.isEnabledFor(DEBUG_LOG_LEVEL):
            self.log(DEBUG_LOG_LEVEL, message, *args, **kwargs)

    def db(self, message, *args, **kwargs) -> None:
        if self.isEnabledFor(DB_LEVEL):
            self.log(DB_LEVEL, message, *args, **kwargs)

    def bot(self, message, *args, **kwargs) -> None:
        if self.isEnabledFor(BOT_LEVEL):
            self.log(BOT_LEVEL, message, *args, **kwargs)


def run_rainbow(level: int = logging.DEBUG) -> RainbowLogger:
    handler = logging.StreamHandler()
    handler.setFormatter(ColoramaFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    return RainbowLogger(logging.getLogger("mycloud"), {})


if __name__ == "__main__":
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
