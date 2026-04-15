import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging(app):
    log_file = os.path.join(LOG_DIR, "app.log")
    abs_log_file = os.path.abspath(log_file)

    for handler in app.logger.handlers:
        if isinstance(handler, RotatingFileHandler) and getattr(handler, 'baseFilename', None) == abs_log_file:
            return

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    app.logger.info("Logging initialized")