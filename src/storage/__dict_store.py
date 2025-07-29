from . import BaseAlertStore


class DictStore(BaseAlertStore):
    def __init__(self, url: str) -> None:
        self.store = {}
        self.id = url  # for this class this url is used as an identifier.
        self.active = set()

    async def put(self, id, alert) -> bool:
        self.store[id] = [alert, self.store.get(id, [None, 0])[1] + 1]
        if id in self.active:
            return False

        self.active.add(id)
        return True

    async def get(self, id):
        return self.store.get(id, [None, 0])

    async def has(self, id):
        return id in self.store

    async def get_count(self, id):
        return self.store.get(id, [None, 0])[1]

    async def remove(self, id):
        self.store[id][1] = 0

    async def purge_active(self, id):
        self.active.remove(id)
        return
