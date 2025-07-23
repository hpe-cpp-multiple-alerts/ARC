from datetime import datetime, timezone

from . import GraphNode


def change_to_date(t_str):
    # Accepts both with and without milliseconds
    # try:
    #     return datetime.strptime(t_str, "%Y-%m-%dT%H:%M:%S.%f").replace(
    #         tzinfo=timezone.utc
    #     )
    # except ValueError:
    #     return datetime.strptime(t_str, "%Y-%m-%dT%H:%M:%S").replace(
    #         tzinfo=timezone.utc
    #     )

    return datetime.strptime(t_str, "%m-%d-%Y").replace(tzinfo=timezone.utc)


class Alert:
    def __init__(self, alert_json: dict) -> None:
        self.unq_id = alert_json["Id"]
        self.severity = alert_json["Current State"]

        self.alert = alert_json
        self.service_name = alert_json["Resource Name"]
        self.service = GraphNode.get_id(self.service_name)
        self.startsAt = change_to_date(alert_json["Start Date"])
        self.endsAt = change_to_date(alert_json["End Date"])
        # self.status =
        self.is_root_cause = False

        self.parent_count = 0
        self.parent_id = ""  # gets updated somewhere.

        self.description = alert_json["Metric"]
        self.summary = alert_json["Subject"]

        # self.id = self.__get_id()
        self.id = f"{self.service}.{self.alert['Instance']}"

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
