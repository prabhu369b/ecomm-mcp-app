import logging
from logging.handlers import RotatingFileHandler
import sys
from config.settings import get_settings
import colorlog
from pythonjsonlogger.json import JsonFormatter
from pathlib import Path

class Logger:
    _configured = False

    @classmethod
    def configure(cls):

        if cls._configured:
            return
        
        settings = get_settings()

        root = logging.getLogger()
        root.setLevel(settings.log.level)
        root.handlers.clear()

        if settings.log.use_json:
            formatter = JsonFormatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s"
            )
        else:
            formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                }
            )
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)

        root.addHandler(console)

        # Apply custom formatter to uvicorn logs
        for name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
            logger = logging.getLogger(name)
            logger.handlers = []
            logger.propagate = True

        if settings.log.file:

            Path(settings.log.file).parent.mkdir(parents=True, exist_ok=True)

            file = RotatingFileHandler(
                settings.log.file,
                maxBytes=10*1024*1024,
                backupCount=5
            )
            file.setFormatter(formatter)
            root.addHandler(file)
        cls._configured = True


    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)



