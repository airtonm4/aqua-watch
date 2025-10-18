import logging

# _global_logger = logging.getLogger()
# _global_logger.setLevel(logging.DEBUG)


# create logger
log = logging.getLogger("core")
log.setLevel(logging.DEBUG)

# create console handler and set level to debug
_ch = logging.StreamHandler()
_ch.setLevel(logging.DEBUG)

# create formatter
_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

# add formatter to ch
_ch.setFormatter(_formatter)

# add ch to logger
log.addHandler(_ch)
