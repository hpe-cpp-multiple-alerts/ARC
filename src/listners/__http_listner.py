import logging
import os
from pathlib import Path
from src.models.feedback import FeedBack
from src.notifier import WsNotifier
from . import BaseListener, log
from src.message_queue import BaseMessageQueue
from aiohttp import web
import re

LOCALHOST_ORIGIN_PATTERN = re.compile(r"^http://localhost(:\d+)?$")


@web.middleware
async def cors_middleware(request, handler):
    # Get Origin header (if any)
    origin = request.headers.get("Origin")

    # Handle preflight (OPTIONS) before reaching route handlers
    if request.method == "OPTIONS":
        response = web.Response(status=204)
    else:
        response = await handler(request)

    # Only apply CORS if the origin is from localhost
    if origin and LOCALHOST_ORIGIN_PATTERN.match(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"

    return response


logger = logging.getLogger(__name__)

"""
this is the structure of the alert that will be sent by alertmanager
{
  "version": "4",
  "groupKey": <string>,              // key identifying the group of alerts (e.g. to deduplicate)
  "truncatedAlerts": <int>,          // how many alerts have been truncated due to "max_alerts"
  "status": "<resolved|firing>",
  "receiver": <string>,
  "groupLabels": <object>,
  "commonLabels": <object>,
  "commonAnnotations": <object>,
  "externalURL": <string>,           // backlink to the Alertmanager.
  "alerts": [
    {
      "status": "<resolved|firing>",
      "labels": <object>,
      "annotations": <object>,
      "startsAt": "<rfc3339>",
      "endsAt": "<rfc3339>",
      "generatorURL": <string>,      // identifies the entity that caused the alert
      "fingerprint": <string>        // fingerprint to identify the alert
    },
    ...
  ]
}
"""


class HTTPListener(BaseListener):
    def __init__(self, work_queue: BaseMessageQueue, notifier: WsNotifier) -> None:
        self.work_queue = work_queue
        self.app = web.Application(middlewares=[cors_middleware])
        self.fb_handler = None
        self.w_sockets = set()
        self.notifier = notifier
        self.app.add_routes(
            [
                web.post("/api/alerts", self.receive_alert),
                web.post("/api/feedback", self.receive_feedback),
                web.get("/api/ws", self.web_socket_handler),
                web.delete("/api/batch", self.batch_delete_handler),
            ]
        )

        static_path = Path(os.getcwd()) / "dist"

        async def index(request):
            return web.FileResponse(static_path / "index.html")

        self.app.router.add_route("*", "/", index)
        self.app.router.add_static("/", path=static_path, follow_symlinks=True)

        self.runner = web.AppRunner(self.app)
        self.site = None

    async def listen(self):
        await self.runner.setup()
        host = "0.0.0.0"
        port = 8080
        self.site = web.TCPSite(self.runner, host=host, port=port)
        log.info(f"HTTPListener is running on http://{host}:{port}")
        await self.site.start()

    async def receive_alert(self, request: web.Request):
        try:
            alerts = await request.json()
        except Exception:
            return web.Response(status=400)

        self.work_queue.put_nowait(convert_to_alerts(alerts))

        return web.Response(status=200)

    async def receive_feedback(self, request: web.Request):
        """Processes the feedback from json to custom Feedback type and sends to detector"""
        # add logic to change feedback to normal thing
        fb = FeedBack(await request.json())  # change

        if self.fb_handler:
            self.fb_handler(fb)

        return web.Response(status=200)

    def set_feedback_listner(self, handler):
        self.fb_handler = handler

    async def batch_delete_handler(self, request: web.Request):
        gid = request.query.get("group_id")
        if gid is None:
            return
        await self.notifier.delete_group(gid)
        return web.Response(status=200)

    async def web_socket_handler(self, request: web.Request):
        logger.info("A new ws request arrived.")
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        logger.debug("Upgraded to websocket")
        self.w_sockets.add(ws)

        await self.notifier.add_wsocket(ws)
        logger.debug("sent all batches.")
        async for msg in ws:
            # if an incoming msg, then exit
            break

        await self.notifier.delete_websocket(ws)

        return ws

    async def close(self):
        log.info("Stopping http server.")
        await self.site.stop()


def convert_to_alerts(json_data):
    logger.debug("Alert came processing it.", json_data)
    return json_data["alerts"]
