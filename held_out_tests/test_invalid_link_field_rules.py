from typing import Annotated, List

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import init_beanie

@pytest.mark.asyncio
async def test_invalid_link_field_rules():
    from typing import Annotated

    from beanie import Document, Link, ReferenceDeleteRules

    with pytest.raises(Exception):
        class Door(Document):
            height: int = 2

        class WoodenHouse(Document):
            name: str = "Wooden House"
            door: Annotated[Link[Door], ReferenceDeleteRules.PULL_FROM_LIST]

        client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")

        await init_beanie(
            client.db_name,
            document_models=[Door, WoodenHouse]
        )

