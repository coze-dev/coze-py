import logging

logger = logging.getLogger("cozepy")


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

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    formatter = logging.Formatter("[%(name)s][%(levelname)s][%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.setLevel(level)


log_fatal = logger.fatal
log_error = logger.error
log_warning = logger.warning
log_info = logger.info
log_debug = logger.debug

setup_logging(logging.WARNING)
