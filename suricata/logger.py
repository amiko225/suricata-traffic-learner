import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path


# katalog bazowy projektu
base_dir = Path(__file__).resolve().parent.parent
logs_dir = base_dir / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)  # utwórz folder jeśli nie istnieje

# Logger
logger = logging.getLogger("trafficlearner")
logger.setLevel(logging.INFO)

# Plik logów z rotacją 5 MB, 5 plików
log_filename = logs_dir / "trafficlearner.log"

# Handler
file_handler = TimedRotatingFileHandler(
    log_filename,
    when="D",
    backupCount=60,
    encoding="utf-8"
)

# Formatka
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)