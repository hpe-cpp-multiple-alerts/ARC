from pathlib import Path
import sys
import os


from src.graph.__base import BaseGraph
from src.ingress import PollerIngress
from src.http_server import HTTPServer
from src.storage.__base import BaseAlertStore

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json

from src import log

from src.notifier import WsNotifier
from src.graph import ServiceGraph
from src.message_queue import AsyncQueue
from src.detector import ProbabilityDetector
from src.storage import DictStore
from src.preprocessing.causal_inference import compute_alpha_beta_links
from src.models import Alert


async def preprocess(graph: BaseGraph, store: BaseAlertStore):
    data_path = Path(__file__).parent.parent / "test_data/data"
    alert_jsons = []
    for f in data_path.iterdir():
        with open(f, "r") as fp:
            alerts = json.load(fp)
            alert_jsons.extend(alerts)
    historical_alerts = [Alert(a) for a in alert_jsons]

    # Compute α/β link strengths using valid historical alerts
    precomputed_links = await compute_alpha_beta_links(historical_alerts, store, graph)
    print("Preprocessing summary:")
    print(f"Total historical alerts used: {len(historical_alerts)}")
    print(f"Total computed links: {len(precomputed_links)}")

    print("Head of the computed links.")
    for i, ((src, dst), (alpha, beta)) in enumerate(precomputed_links.items()):
        print(f"Link {i + 1}: {src} → {dst} | α={alpha}, β={beta}")
        if i == 4:
            break

    return precomputed_links


async def main(config):
    notifier = WsNotifier()
    graph = ServiceGraph("test_data/test_service_map.yaml")
    mq = AsyncQueue()
    store = DictStore("test/alerts")
    precomputed_links = await preprocess(graph, store)

    # Initialize detector
    detector = ProbabilityDetector(graph, mq, store, notifier, precomputed_links)
    p_ingress = (
        # 1 minute.
        PollerIngress(mq, 1).with_url("http://localhost:8081").with_token("something")
    )

    httpserver = HTTPServer(notifier, detector.feedback_handler)
    try:
        await asyncio.gather(detector.start(), httpserver.listen(), p_ingress.begin())
    except asyncio.CancelledError:
        print()
        await httpserver.close()
        await notifier.free_wsockets()
        raise
    except Exception as e:
        log.warning(f"Error in system {e}")
        return


def parse_config():
    pass


if __name__ == "__main__":
    try:
        cfg = parse_config()
        asyncio.run(main(cfg))
    except KeyboardInterrupt:
        print("Exiting the application.")
