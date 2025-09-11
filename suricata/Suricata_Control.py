import os
from logger import logger


class SuricataControl:
    """Sterowanie procesem Suricaty."""

    def reload_rules(self):
        """Przeładuj reguły (np. przez systemctl albo SIGHUP)."""
        logger.info("Reloading Suricata rules...")
        ret = os.system("sudo suricatasc -c ruleset-reload-nonblocking")
        if ret == 0:
            logger.info("Suricata rules reloaded.")
        else:
            logger.error(f"Failed to reload Suricata, exit code: {ret}")


''' subprocess wywalał błędy '''