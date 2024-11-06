import logging
import sys
from datetime import datetime


class CustomFormatter(logging.Formatter):

    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',  # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m',  # Magenta
        'RESET': '\033[0m'  # Reset
    }

    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✨',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '💥'
    }

    def format(self,record):
        if not record.exc_info:
            level = record.levelname
            msg = record.msg

            timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

            file_info = f"{record.filename}:{record.lineno}"

            color = self.COLORS.get(level,'')
            emoji = self.EMOJIS.get(level,'')
            reset = self.COLORS.get('RESET','')

            return f"{color}{timestamp} {emoji} [{level}] {file_info} - {msg}{reset}"


        return super().format(record)

class ErrorFilter(logging.Filter):
    def filter(self, record):
        return record.levelname in {"ERROR", "DEBUG", "CRITICAL"}


def setup_logger():

    ## Setup
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    ## Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    ## File Handler
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    file_handler.addFilter(ErrorFilter())
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
logger.info("Logger Setup Complete!")