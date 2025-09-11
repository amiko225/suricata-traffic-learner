from Suricata_Control import SuricataControl
from Suricata_Rules import SuricataRules
from Alert_Monitor import SuricataAlertMonitor
from async_tasks import batch_add_rules
from helpers import create_learning_rules, create_rule_from_alert, clear_file
from logger import logger

import asyncio
import signal
import sys


PASS_RULES_PATH = "/etc/suricata/rules/pass.rules"
LEARN_RULES_PATH = "/etc/suricata/rules/learn.rules"
LEARN_ALERTS_PATH = "/var/log/suricata/learn_alerts.json"

ip_addr = [
    ("192.168.0.0/24", "192.168.44.0/24")
]


# Globalne obiekty dla handlera sygnałów - potrzebne dla systemd
loop = asyncio.get_event_loop()
stop_event = asyncio.Event()


async def main_loop(pass_rules, learn_alerts, suricata_control, batch_time=60):
    new_rules_queue = asyncio.Queue()

    def handle_alert(alert):
        learned_rule = create_rule_from_alert(alert)
        new_rules_queue.put_nowait(learned_rule)
        logger.info(f"Queued new rule from alert: {learned_rule}")

    learn_alerts.on_new_alert = handle_alert

    tasks = [
        asyncio.create_task(batch_add_rules(pass_rules, suricata_control, new_rules_queue, batch_time)),
        asyncio.create_task(learn_alerts.run())
    ]

    # Czekaj aż stop_event zostanie ustawiony sygnałem
    await stop_event.wait()

    logger.info("Wyłączanie, anulowanie tasków...")
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    # Czyszczenie plików i reload Suricaty
    clear_file(LEARN_RULES_PATH)
    clear_file(LEARN_ALERTS_PATH)
    suricata_control.reload_rules()
    logger.info("Pliki learn.rules i learn_alerts.json wyczyszczone.")


def handle_exit(signum, frame):
    logger.info(f"Otrzymano sygnał {signum}, kończę...")
    stop_event.set()


if __name__ == "__main__":

    logger.info("Startuję logger")

    # Inicjalizacja obiektów
    pass_rules = SuricataRules(PASS_RULES_PATH)
    learn_rules = SuricataRules(LEARN_RULES_PATH, sid_start=2000001)
    learn_alerts = SuricataAlertMonitor(LEARN_ALERTS_PATH)
    suricata_control = SuricataControl()

    # Przypisanie handlerów sygnałów
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    # Reguły uczące
    learning_rules = create_learning_rules(ip_addr)
    for rule in sorted(learning_rules, key=lambda r: str(r.src_ip)):
        learn_rules.add_rule(rule)
    suricata_control.reload_rules()

    try:
        loop.run_until_complete(main_loop(pass_rules, learn_alerts, suricata_control, batch_time=60))
    except Exception as e:
        logger.exception(f"Nieoczekiwany błąd: {e}")
    finally:
        loop.close()
        logger.info("Program zakończony.")
