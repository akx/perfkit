import logging

from perfkit.query_tracker import QueryTracker


class DjangoQueryTrackerLogHandler(logging.Handler):
    def __init__(self, query_tracker: QueryTracker) -> None:
        super().__init__(level=logging.DEBUG)
        self.query_tracker = query_tracker

    def handle(self, record: logging.LogRecord) -> bool:
        if "args=" not in record.msg:
            return False
        # TODO: figure out how to forcibly enable stack_info
        self.query_tracker.record(record.getMessage(), record.stack_info)
        return True


def prepare_logging(tracker: QueryTracker, depropagate=False):
    logger = logging.getLogger("django.db.backends")
    logger.setLevel(logging.DEBUG)
    logger.handlers = [DjangoQueryTrackerLogHandler(tracker)]
    if depropagate:
        logger.propagate = False
