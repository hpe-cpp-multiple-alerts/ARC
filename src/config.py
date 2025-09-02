from datetime import timedelta
from pathlib import Path
import sys
from attr import dataclass
import yaml


@dataclass
class Polling:
    token: str = ""
    url: str = ""
    interval: int = 60  # 1 minute.
    max_failures = 10


@dataclass
class Detector:
    batch_gap_threshold: timedelta = timedelta(minutes=15)
    time_delta: timedelta = timedelta(minutes=5)
    confidence_threshold: float = 0.2

    initial_alpha: int = 1
    initial_beta: int = 1

    delay: int = 5


@dataclass
class Server:
    host: str = "0.0.0.0"
    port: int = 8080


@dataclass
class Store:
    path: str = "test/alerts"


@dataclass
class ServiceGraph:
    path: str = "service_dependancy_map.yaml"


@dataclass
class HistoricData:
    path: Path = Path()


@dataclass
class AppConfig:
    polling: Polling
    detector: Detector
    server: Server
    store: Store
    historic_data: HistoricData
    service_graph: ServiceGraph


def load_config(path: str) -> AppConfig:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    raw["detector"]["time_delta"] = timedelta(minutes=raw["detector"]["time_delta"])
    raw["detector"]["batch_gap_threshold"] = timedelta(
        minutes=raw["detector"]["batch_gap_threshold"]
    )
    raw["historic_data"] = raw.get("historic_data", {})
    path = raw["historic_data"].get("path", "")
    raw["historic_data"]["path"] = Path(path)

    return AppConfig(
        detector=Detector(**raw.get("detector", {})),
        polling=Polling(**raw.get("polling", {})),
        server=Server(**raw.get("server", {})),
        store=Store(**raw.get("store", {})),
        historic_data=HistoricData(**raw.get("historic_data", {})),
        service_graph=ServiceGraph(**raw.get("service_graph", {})),
    )


cfg_path = "config.yaml" if len(sys.argv) <= 1 else sys.argv[1]
cfg_path = "config.yaml" if not cfg_path else cfg_path  # check full null value.
cfg = load_config(cfg_path)
