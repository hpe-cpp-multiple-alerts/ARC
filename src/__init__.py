class Constants:
    pass


import logging

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s - %(module)s - %(message)s"
)

log = logging.getLogger(__name__)
