import logging

logger = logging.getLogger("cozepy")

# config logger
formatter = logging.Formatter("[cozepy][%(levelname)s][%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.propagate = False
logger.addHandler(handler)


def setup_logging(level: int = logging.WARNING) -> None:
    if level not in [
        logging.FATAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
        logging.NOTSET,
    ]:
        raise ValueError(f"invalid log level: {level}")

    logger.setLevel(level)


log_fatal = logger.fatal
log_error = logger.error
log_warning = logger.warning
log_info = logger.info
log_debug = logger.debug

setup_logging(logging.WARNING)
