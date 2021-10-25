import logging
from rich.logging import RichHandler

handler = RichHandler()
formatter = logging.Formatter("%(message)s")
logger = logging.getLogger("kaunseling")

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False
