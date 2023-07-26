import sys
from logging import getLogger, Logger, Formatter, StreamHandler, DEBUG

_is_configured: bool = False


def configure_logging(level: int = DEBUG) -> None: 
    global _is_configured
    if _is_configured:
        return

    # Reconfiguring the logger here will also affect test running in the PyCharm IDE (i.e. IntelliJ Python plugin)
    logger: Logger = getLogger()
    logger.setLevel(level)
    formatter: Formatter = Formatter('%(relativeCreated)d (%(name)s) | %(levelname)s | [%(module)s:%(lineno)s] | %(funcName)s | %(message)s')
    console_handler: StreamHandler = StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    _is_configured = True

