import sys
from logging import Logger, Formatter, StreamHandler, Filter, LogRecord
from logging import  getLogger, addLevelName, getLevelName
from logging import  DEBUG, INFO

"""
https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library

Note It is strongly advised that you do not log to the root logger in your library. Instead, use a logger with a unique and easily identifiable name, such as the __name__ for your library’s top-level package or module. Logging to the root logger will make it difficult or impossible for the application developer to configure the logging verbosity or handlers of your library as they wish.
"""
_is_configured: bool = False

# Define TRACE  log level
TRACE = 1

# "Register" new loggin level
addLevelName(TRACE, 'TRACE') 

# Verify
assert getLevelName(TRACE) == 'TRACE'


def configure_logging(level: int = DEBUG) -> None: 
    global _is_configured
    if _is_configured:
        return

    # Reconfiguring the logger here will also affect test running in the PyCharm IDE (i.e. IntelliJ Python plugin)
    # and VS Code IDE
    root_logger: Logger = getLogger()
    root_logger.setLevel(level)
    formatter: Formatter = Formatter('%(relativeCreated)d (%(name)s) | %(levelname)s | [%(module)s:%(lineno)s] | %(funcName)s | %(message)s')
    console_handler: StreamHandler = StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    introspect_logger: Logger = getLogger("common.introspect")
    introspect_logger.setLevel(INFO)

    page_dump_logger: Logger = getLogger("roampub.page_dump")
    page_dump_logger.setLevel(level)

    roam_model_logger: Logger = getLogger("roampub.roam_model")
    roam_model_logger.setLevel(level)

    _is_configured = True


class FunctionFilter(Filter):
    """
    Filters *out* ``LogRecord`` based on function name
    """
    def __init__(self, function_names: list[str]):
        self._function_names = function_names

    def filter(self, record: LogRecord) -> bool:
        return not record.funcName in self._function_names
