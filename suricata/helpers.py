from Rule import Rule
from Alert import Alert
from ipaddress import IPv4Network
from logger import logger


def create_learning_rules(ip_pairs: list[tuple[str, str]]) -> list[Rule]:
    """Tworzy listę reguł uczących na podstawie podanych par IP."""
    rules = []
    for src, dst in ip_pairs:
        rule = Rule(
            action=Rule.Actions.ALERT,
            src_ip=IPv4Network(src),
            dst_ip=IPv4Network(dst),
            protocol=Rule.Protocols.IP,
            src_port="any",
            dst_port="any",
            direction="<>",
            options={"msg": f'"Learning traffic from {src} -> {dst}"'}
        )
        rules.append(rule)
    return rules

def create_rule_from_alert(alert: Alert) -> Rule:
    """Tworzy regułę PASS na podstawie alertu."""
    return Rule(
        action=Rule.Actions.PASS,
        src_ip=alert.src_ip,
        dst_ip=alert.dst_ip,
        protocol=Rule.Protocols.IP,
        src_port="any",
        dst_port="any",
        direction="<>",
        options={"msg": f'"Learned rule from alert: {alert.alert_msg}"'}  # SID dodany przez SuricataRules
    )

def clear_file(file_path: str):
    """Czyści zawartość pliku."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.truncate(0)
        logger.info(f"Cleared file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to clear file {file_path}: {e}")