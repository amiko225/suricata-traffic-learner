from enum import Enum
from ipaddress import IPv4Network, ip_network

class Rule:

    ##########################################
    # Enums jako podklasy
    ##########################################
    class Actions(Enum):
        PASS = "pass"
        DROP = "drop"
        ALERT = "alert"
        REJECT = "reject"

    class Protocols(Enum):
        IP = "ip"
        TCP = "tcp"
        UDP = "udp"
        ICMP = "icmp"
        DNS = "dns"

    ##########################################
    # Metody pomocnicze
    ##########################################
    @staticmethod
    def normalize_ip_pair(src: IPv4Network, dst: IPv4Network) -> tuple[IPv4Network, IPv4Network]:
        """Zwraca parę IP w uporządkowanej kolejności, aby <> traktować jako jednolitą."""
        if int(src.network_address) <= int(dst.network_address):
            return src, dst
        else:
            return dst, src

    ##########################################
    # Parser z tekstu
    ##########################################
    @classmethod
    def from_text(cls, line: str):
        parts = line.split()
        parsed_action = parts[0]
        parsed_protocol = parts[1]
        parsed_src_ip = parts[2]
        parsed_src_port = parts[3]
        parsed_direction = parts[4]
        parsed_dst_ip = parts[5]
        parsed_dst_port = parts[6]
        options_str = ' '.join(parts[7:]).strip("()")

        action = cls.Actions(parsed_action)
        protocol = cls.Protocols(parsed_protocol)
        src_ip = ip_network(parsed_src_ip, strict=True)
        dst_ip = ip_network(parsed_dst_ip, strict=True)
        src_port = parsed_src_port
        dst_port = parsed_dst_port
        direction = parsed_direction

        options = {}
        if options_str:
            for opt in options_str.split(";"):
                opt = opt.strip()
                if not opt:
                    continue
                if ":" in opt:
                    k, v = opt.split(":", 1)
                    options[k.strip()] = v.strip()

        return cls(
            action=action,
            src_ip=IPv4Network(src_ip),
            dst_ip=IPv4Network(dst_ip),
            protocol=protocol,
            src_port=src_port,
            dst_port=dst_port,
            direction=direction,
            options=options
        )

    ##########################################
    # Konstruktor
    ##########################################
    def __init__(
        self,
        action: Actions,
        src_ip: IPv4Network,
        dst_ip: IPv4Network,
        protocol: Protocols = Protocols.IP,
        src_port: str = "any",
        direction: str = "<>",
        dst_port: str = "any",
        options=None
    ):
        if direction == "<>":
            src_ip, dst_ip = self.normalize_ip_pair(src_ip, dst_ip)

        if not isinstance(action, self.Actions):
            raise ValueError(f"action must be an instance of Actions enum, got {action}")

        if not isinstance(protocol, self.Protocols):
            raise ValueError(f"protocol must be an instance of Protocols enum, got {protocol}")

        self.action = action
        self.protocol = protocol.value
        self.src_ip = src_ip
        self.src_port = src_port
        self.direction = direction
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.options = dict(options) if options else {}

    ##########################################
    # Metody instancyjne
    ##########################################
    def to_text(self) -> str:
        options_str = " ".join(f"{k}:{v};" for k, v in self.options.items())
        return (
            f"{self.action.value} {self.protocol} {self.src_ip} {self.src_port} "
            f"{self.direction} {self.dst_ip} {self.dst_port} "
            f"({options_str})"
        )

    def __eq__(self, other) -> bool:
        if self.protocol != other.protocol:
            return False
        return (
            (self.src_ip == other.src_ip and self.dst_ip == other.dst_ip) or
            (self.src_ip == other.dst_ip and self.dst_ip == other.src_ip)
        )

    def __str__(self) -> str:
        return self.to_text()