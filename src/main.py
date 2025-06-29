from pathlib import Path
import sys
import os

from src.graph.__base import BaseGraph
from src.storage.__base import BaseAlertStore

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json

from src.notifier import WsNotifier
from src.graph import ServiceGraph
from src.listners import HTTPListener
from src.message_queue import AsyncQueue
from src.detector import ProbabilityDetector
from src.storage import DictStore
from src.preprocessing.causal_inference import compute_alpha_beta_links
from src.models.alert import Alert


async def preprocess(graph: BaseGraph, store: BaseAlertStore):
    data_path = Path(__file__).parent.parent / "test_data/data"
    alert_jsons = []
    for f in data_path.iterdir():
        with open(f, "r") as fp:
            alerts = json.load(fp)
            alert_jsons.extend(alerts)
    historical_alerts = [Alert(a) for a in alert_jsons]
    for a in historical_alerts:
        await store.put(a.id, a)

    # Compute α/β link strengths using valid historical alerts
    precomputed_links = compute_alpha_beta_links(historical_alerts, graph)
    print("Preprocessing summary:")
    print(f"Total historical alerts used: {len(historical_alerts)}")
    print(f"Total computed links: {len(precomputed_links)}")

    for i, ((src, dst), (alpha, beta)) in enumerate(precomputed_links.items()):
        print(f"Link {i + 1}: {src} → {dst} | α={alpha}, β={beta}")
        if i == 4:
            break

    return precomputed_links


async def main():
    notifier = WsNotifier()
    graph = ServiceGraph("test_data/test_service_map.yaml")
    mq = AsyncQueue()
    store = DictStore("test/alerts")

    precomputed_links = await preprocess(graph, store)

    # Initialize detector
    detector = ProbabilityDetector(graph, mq, store, notifier, precomputed_links)

    # Set up listener and start services
    httpserver = HTTPListener(mq, notifier)
    httpserver.set_feedback_listner(detector.feedback_handler)
    await asyncio.gather(detector.start(), httpserver.listen())


if __name__ == "__main__":
    asyncio.run(main())
