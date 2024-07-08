"""
TODO: sphinx docstring
"""


class BaseStorage:
    def __init__(self):
        self.storage_pool = {}

    def storage_save(self, kin_id, content):
        pass

    async def storage_load(self, kin_id: str, table: str):
        pass

    def storage_alloc(self, kin_id):
        pass

    def storage_clear(self, kin_id):
        pass
