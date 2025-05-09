import logging
import sys


def setup_test_logging():
    """Disable logging during tests."""
    # Remove all handlers from root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set level to CRITICAL for all loggers
    root_logger.setLevel(logging.CRITICAL)

    # Set level to CRITICAL for all loggers
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.setLevel(logging.CRITICAL)
        logger.propagate = True


# Check if we're running tests
if "unittest" in sys.modules:
    setup_test_logging()
