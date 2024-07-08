"""
TODO: sphinx docstring
TODO: externalise the database connection details
"""

import os
from surrealdb import Surreal
from contextlib import asynccontextmanager

from kin_sdk.module.storage.base import BaseStorage
from kin_sdk.common import logger


@asynccontextmanager
async def setup_surrealdb_connection():
    """
    Asynchronous context manager for SurrealDB connection.

    :param url: The URL of the SurrealDB instance.
    :param user: The username for authentication.
    :param password: The password for authentication.
    :param namespace: The namespace to use.
    :param database: The database to use.
    :return: The connected and authenticated SurrealDB client.
    """
    url: str = os.getenv("SURREAL_URL")
    user: str = os.getenv("SURREAL_USER")
    password: str = os.getenv("SURREAL_PASSWORD")
    namespace: str = os.getenv("SURREAL_NAMESPACE")
    database: str = os.getenv("SURREAL_DATABASE")
    db = Surreal(url)
    await db.connect()
    await db.signin({"user": user, "pass": password})
    await db.use(namespace, database)
    try:
        yield db
    finally:
        await db.close()


class DBStorage(BaseStorage):
    def __init__(self):
        pass

    def storage_save(self, kin_id, content):
        pass

    async def storage_load(self, kin_id: str, table: str):
        """
        This method loads the data from the database.
        """
        result = None
        try:
            async with setup_surrealdb_connection() as db:
                # Assign the variable on the connection
                result = await db.query(
                    "SELECT * FROM type::table($tb) WHERE kin_id=type::thing($kid)",
                    {
                        "tb": table,
                        "kid": f"kins:{kin_id}",
                    },
                )
                result = result[0].get("result", None)
        except Exception as e:
            logger.error(f"Error loading data from the database: {e}")
        finally:
            return result

    def storage_alloc(self, kin_id):
        pass

    def storage_clear(self, kin_id):
        pass
