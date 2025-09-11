from ipaddress import IPv4Network
from logger import logger
from Rule import Rule



class SuricataRules:
    def __init__(self, file_path: str, sid_start: int = 1000001):
        self.file_path = file_path
        self.rules: list[Rule] = []
        self.sid_start = sid_start
        self._load_rules()

    def _load_rules(self):
        """Wczytaj reguły z pliku (jeśli istnieje)."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        try:
                            rule = Rule.from_text(line)
                            self.rules.append(rule)
                        except Exception as e:
                            logger.warning(f"Could not parse rule: {line} ({e})")
        except FileNotFoundError:
            logger.info(f"Rules file '{self.file_path}' not found, starting with empty list.")

        # Po wczytaniu posortuj po SID (domyślnie 0, jeśli brak)
        self.rules.sort(key=lambda r: int(r.options.get("sid", 0)))

    def _save_rules(self):
        """Zapisz wszystkie reguły do pliku."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            for rule in self.rules:
                f.write(rule.to_text() + "\n")

    def add_rule(self, rule: Rule):
        # sprawdzenie duplikatu niezależnie od kierunku
        for existing_rule in self.rules:
            if rule == existing_rule:
                logger.info(f"Duplicate rule, not adding: {rule}")
                return False

        if "sid" not in rule.options:
            existing_sids = [int(r.options.get("sid", 0)) for r in self.rules if "sid" in r.options]        # ??
            next_sid = max(existing_sids, default=self.sid_start - 1) + 1
            rule.options["sid"] = next_sid

        self.rules.append(rule)
        self.rules.sort(key=lambda r: int(r.options.get("sid", 0)))
        self._save_rules()
        return True

    def get_rules(self) -> list[Rule]:
        return self.rules

    def delete_all_rules(self):
        self.rules = []
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.truncate(0)  # wyczyszczenie pliku