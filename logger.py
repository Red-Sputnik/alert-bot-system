import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("system.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("alert_bot")
