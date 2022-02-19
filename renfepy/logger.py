import logging

# Config logging
logging.basicConfig(
    filename="/var/log/renfe_search.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
log = logging
