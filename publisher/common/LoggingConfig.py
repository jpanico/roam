import sys
import logging

_is_configured: bool = False


def configure_logging(level: int = logging.DEBUG):
    global _is_configured
    if _is_configured:
        return

    # Reconfiguring the logger here will also affect test running in the PyCharm IDE (i.e. IntelliJ Python plugin)
    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = logging.Formatter('%(relativeCreated)d (%(name)s) | %(levelname)s | [%(module)s:%(lineno)s] | %(funcName)s | %(message)s')
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    _is_configured = True

