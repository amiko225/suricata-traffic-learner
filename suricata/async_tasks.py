from datetime import datetime, timedelta
from Suricata_Rules import SuricataRules
from Suricata_Control import SuricataControl
import asyncio
from logger import logger


async def batch_add_rules(
    pass_rules: SuricataRules,
    suricata_control: SuricataControl,
    new_rules_queue: asyncio.Queue,
    batch_time: int = 60
):
    """
    Zbiera nowe reguły z `new_rules_queue` przez `batch_time` sekund,
    dodaje je do pass_rules naraz i przeładowuje Suricatę.
    """

#try:
    while True:
        end_time = datetime.now() + timedelta(seconds=batch_time)
        batch_rules = []

        logger.info(f"Starting batch collection of new rules for {batch_time} seconds...")

        while datetime.now() < end_time:
            try:
                # Pobiera regułę z kolejki z timeoutem 0.5s
                rule = await asyncio.wait_for(new_rules_queue.get(), timeout=0.5)
                batch_rules.append(rule)
            except asyncio.TimeoutError:
                continue  # jeśli brak reguł, po prostu sprawdzamy czas ponownie

        # Dodajemy nowe reguły do pass_rules, ignorując duplikaty
        added_count = 0
        for rule in batch_rules:
            if pass_rules.add_rule(rule):  # add_rulpowinna zwracać True jeśli dodano nową regułęe
                added_count += 1

        if added_count > 0:
            suricata_control.reload_rules()
            logger.info(f"Added {added_count} new rules in batch and reloaded Suricata.")
        else:
            logger.info("No new rules to add in batch.")
