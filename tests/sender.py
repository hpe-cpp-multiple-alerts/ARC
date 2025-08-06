# all the alerts should relate to the same service is not working.
import requests

alerts_with_noise = [
    [
        # Base
        [
            {
                "labels": {
                    "job": "product-catalog-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T00:00:00",
                "endsAt": "2025-06-29T00:03:00",
                "status": "firing",
                "annotations": {
                    "description": "Metadata sync delay",
                    "summary": "product-catalog-service experienced 'Metadata sync delay'",
                },
            },
            {
                "labels": {
                    "job": "inventory-service",
                    "instance": "2",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T00:00:30",
                "endsAt": "2025-06-29T00:03:30",
                "status": "firing",
                "annotations": {
                    "description": "Update failure increase",
                    "summary": "inventory-service experienced 'Update failure increase'",
                },
            },
            {
                "labels": {
                    "job": "order-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T00:01:00",
                "endsAt": "2025-06-29T00:04:00",
                "status": "firing",
                "annotations": {
                    "description": "Order backlog risk",
                    "summary": "order-service experienced 'Order backlog risk'",
                },
            },
            {
                "labels": {
                    "job": "payment-service",
                    "instance": "1",
                    "severity": "critical",
                },
                "startsAt": "2025-06-29T00:01:30",
                "endsAt": "2025-06-29T00:04:30",
                "status": "firing",
                "annotations": {
                    "description": "Gateway timeout spike",
                    "summary": "payment-service experienced 'Gateway timeout spike'",
                },
            },
        ],
    ],
]

SCENARIO = 0
pattren = [
    *alerts_with_noise[SCENARIO],
]

requests.post("http://localhost:9090/webhook/alerts", json={"alerts": pattren})
