from typing import Annotated

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import init_beanie

@pytest.mark.asyncio
async def test_set_null_rule_exception():
    from typing import Annotated

    from beanie import Document, Link, ReferenceDeleteRules

    class Door(Document):
        height: int = 2

    with pytest.raises(Exception):
        class WoodenHouse(Document):
            name: str = "Wooden House"
            door: Annotated[Link[Door], ReferenceDeleteRules.SET_NULL]

        client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")

        await init_beanie(
            client.db_name,
            document_models=[Door, WoodenHouse]
        )
