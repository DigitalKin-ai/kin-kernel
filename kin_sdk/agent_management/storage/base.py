"""
TODO: sphinx docstring
"""


class BaseStorage:
    """TODO: sphinx docstring"""

    def __init__(self):
        self.storage_pool = {}

    def storage_save(self, kin_id, content):
        """TODO: sphinx docstring"""

    async def storage_load(self, kin_id: str, table: str):
        """TODO: sphinx docstring"""

    def storage_alloc(self, kin_id):
        """TODO: sphinx docstring"""

    def storage_clear(self, kin_id):
        """TODO: sphinx docstring"""
