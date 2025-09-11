from ipaddress import IPv4Network


class Alert:
    def __init__(
        self,
        timestamp: str,
        alert_msg: str,
        src_ip: IPv4Network,
        src_port: str,
        dst_ip: IPv4Network,
        dst_port: str,
        protocol: str
    ):

        self.timestamp = timestamp
        self.alert_msg = alert_msg
        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.protocol = protocol

    def __str__(self) -> str:
        return (
            f"[{self.timestamp}] {self.alert_msg} | "
            f"{self.src_ip}:{self.src_port} -> {self.dst_ip}:{self.dst_port} "
            f"({self.protocol})"
        )
