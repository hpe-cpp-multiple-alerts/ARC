from datetime import datetime, timezone
import hashlib

from . import GraphNode


def change_to_timestamp(t_str):
    return datetime.strptime(t_str.replace(" IST", ""), "%b %d, %Y, %I:%M:%S %p")


def change_to_date(t_str):
    # Accepts both with and without milliseconds
    return datetime.strptime(t_str, "%m-%d-%Y").replace(tzinfo=timezone.utc)


class Alert:
    def __init__(self, alert_json: dict) -> None:
        self.unq_id = alert_json["Id"]
        self.severity = alert_json["Current State"]

        self.alert = alert_json
        self.service_name = alert_json["Resource Name"]
        self.service = GraphNode.get_id(self.service_name)
        self.startsAt = change_to_timestamp(alert_json["Created Time"])
        self.endsAt = change_to_date(alert_json["End Date"])
        # self.status =
        self.is_root_cause = False

        self.parent_count = 0
        self.parent_id = ""  # gets updated somewhere.

        self.description = alert_json["Metric"]
        self.summary = alert_json["Subject"]

        self.id = self.__get_id()
        # self.id = f"{self.service}.{self.alert['Instance']}"

    def __str__(self) -> str:
        return f"Alert from service {self.service_name} with name `{self.description}` started at {self.startsAt} with severity {self.severity}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "service": self.service_name,
            "summary": self.description,
        }

    def __repr__(self) -> str:
        return self.id

    def __get_id(self) -> str:
        s = f"{self.service}.{self.alert['Instance']}"
        h = hashlib.sha256(s.encode()).digest()
        return str(int.from_bytes(h, "big"))[:15]
