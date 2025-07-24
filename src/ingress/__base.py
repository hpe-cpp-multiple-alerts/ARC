from abc import ABC, abstractmethod
from src.message_queue import BaseMessageQueue


class BaseIngress(ABC):
    @abstractmethod
    def __init__(self, work_queue: BaseMessageQueue) -> None:
        self.mq = work_queue

    @abstractmethod
    async def begin(self):
        """this is to starts the process of putting the alerts in message queue."""

    @abstractmethod
    async def stop(self):
        """Converse of stop"""
