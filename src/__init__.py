class Constants:
    pass


import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)s - %(module)s - %(message)s"
)

log = logging.getLogger(__name__)
