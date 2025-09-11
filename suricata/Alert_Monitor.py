import asyncio
import json
from typing import Callable, Optional
from ipaddress import IPv4Network

from Alert import Alert

from logger import logger


class SuricataAlertMonitor:

    def __init__(self, alert_file: str):
        self.alert_file = alert_file
        self.alert_read_command = ["tail", "-n", "0", "-f", self.alert_file]
        self.on_new_alert: Optional[Callable[[Alert], None]] = None
        self.proc = None

    async def read_stdout(self, stdout):
        logger.info(f"Reading Suricata alerts from {self.alert_file}...")
        while True:
            line = await stdout.readline()
            if not line:
                await asyncio.sleep(0.1)
                continue

            try:
                data = json.loads(line.decode().strip())
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON line: {line}")
                continue

            if data.get("event_type") == "alert":
                alert = self.parse_alert(data)
                if alert and callable(self.on_new_alert):
                    try:
                        self.on_new_alert(alert)
                    except Exception as e:
                        logger.error(f"Error in on_new_alert callback: {e}")

    async def read_stderr(self, stderr):
        logger.debug("Reading stderr...")
        while True:
            buf = await stderr.read()       # może/musi być readline() ?
            if not buf:
                break
            logger.error(f"Stderr: {buf.decode()}")

    def parse_alert(self, data: dict) -> Optional[Alert]:
        """Parsuje JSON Suricaty do obiektu Alert."""
        try:
            alert = data["alert"]
            return Alert(
                timestamp=data.get("timestamp", "unknown"),
                alert_msg=alert.get("signature", "no-msg"),
                src_ip=IPv4Network(data.get("src_ip", "0.0.0.0")),
                src_port=str(data.get("src_port", "any")),
                dst_ip=IPv4Network(data.get("dest_ip", "0.0.0.0")),
                dst_port=str(data.get("dest_port", "any")),
                protocol=data.get("proto", "ip"),
            )
        except Exception as e:
            logger.error(f"Failed to parse alert: {e}")
            return None


    async def run(self):
        self.proc = await asyncio.create_subprocess_exec(
            *self.alert_read_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            await asyncio.gather(
                self.read_stdout(self.proc.stdout),
                self.read_stderr(self.proc.stderr),
            )
        except asyncio.CancelledError:
            logger.debug(f"Stopping read alert file {self.alert_file}...")
            raise
        finally:
            if self.proc:
                self.proc.terminate()
            try:
                await self.proc.wait()
            except Exception as e:
                logger.warning(f"Failed to wait for subprocess termination: {e}")
            logger.info("Alert monitor subprocess closed")
