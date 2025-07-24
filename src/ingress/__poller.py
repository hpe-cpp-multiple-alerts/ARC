import asyncio
import logging

import aiohttp
from src.ingress import convert_to_alerts
from . import BaseIngress
from src.message_queue import BaseMessageQueue
from src.config import cfg

log = logging.getLogger(__name__)

MAX_FAILURES = cfg.polling.max_failures


class PollerIngress(BaseIngress):
    def __init__(self, work_queue: BaseMessageQueue, interval: int) -> None:
        super().__init__(work_queue)
        self.failures = 0
        self.url = ""
        self.token = ""
        self.interval = interval

    def with_url(self, url):
        self.url = url
        return self

    def with_token(self, token):
        self.token = token
        return self

    async def begin(self):
        while True:
            alerts = await self.get()
            await self.put_in_mq(alerts)
            await asyncio.sleep(self.interval)

    async def get(self) -> list[dict]:
        # http call to the url.
        headers = {"Authorization": f"Bearer {self.token}"}

        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.get(self.url) as response:
                    if response.status != 200:
                        raise Exception("temp")
                    data = await response.json()
                    return convert_to_alerts(data)
            except asyncio.CancelledError:
                raise
            except Exception:
                self.failures += 1
                log.info(f"Get failure while pollig alerts failures={self.failures}")
                if self.failures > MAX_FAILURES:
                    raise Exception(
                        f"Cannot fetch alerts from the source url={self.url}, token={self.token}"
                    )
                return []

    async def put_in_mq(self, alerts: list[dict]):
        await self.mq.put(alerts)

    async def stop(self):
        return await super().stop()
