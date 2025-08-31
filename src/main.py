from pathlib import Path
import sys
import os


from src.graph import BaseGraph
from src.http_server import HTTPServer
from src.ingress import HTTPIngress
from src.storage import BaseAlertStore

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


async def preprocess(graph: BaseGraph, store: BaseAlertStore, data_path: Path):
    if not data_path.exists():
        log.info(
            f"Skipping preprocessing as the directory is not present in the disk path={data_path.absolute()}"
        )
        return

    alert_jsons = []
    for f in data_path.iterdir():
        with open(f, "r") as fp:
            alerts = json.load(fp)
            alert_jsons.extend(alerts)
    historical_alerts = list(
        filter(lambda x: x.service != -1, (Alert(a) for a in alert_jsons))
    )

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
    graph = ServiceGraph(cfg.service_graph.path)
    mq = AsyncQueue()
    store = DictStore(cfg.store.path)
    # precomputed_links = await preprocess(graph, store, cfg.historic_data.path)
    precomputed_links = {}

    # Initialize detector
    store.active.clear()
    detector = ProbabilityDetector(graph, mq, store, notifier, precomputed_links)
    # p_ingress = (
    #     # 1 minute.
    #     PollerIngress(mq, 1).with_url(cfg.polling.url).with_token(cfg.polling.token)
    # )

    h_ingress = HTTPIngress(mq)

    httpserver = HTTPServer(notifier, detector.feedback_handler)
    try:
        await asyncio.gather(detector.start(), httpserver.listen(), h_ingress.begin())
    except asyncio.CancelledError:
        print()
        await httpserver.close()
        await notifier.free_wsockets()
        raise
    except Exception as e:
        log.warning(f"Error in system {e}")
        raise


if __name__ == "__main__":
    try:
        from src.config import cfg

        asyncio.run(main(cfg))
    except KeyboardInterrupt:
        print("Exiting the application.")
