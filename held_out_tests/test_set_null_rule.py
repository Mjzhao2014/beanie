from typing import Annotated

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import init_beanie

@pytest.mark.asyncio
async def test_set_null_rule():
    from typing import Annotated, Optional

    from beanie import Document, Link, ReferenceDeleteRules

    class Door(Document):
        height: int = 2

    class WoodenHouse(Document):
        name: str = "Wooden House"
        door: Annotated[Optional[Link[Door]], ReferenceDeleteRules.SET_NULL]

    client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")

    await init_beanie(
        client.db_name,
        document_models=[Door, WoodenHouse]
    )

    door1 = await Door().insert()
    wooden_house = await WoodenHouse(door=door1).insert()
    await door1.delete()

    wooden_house = await WoodenHouse.get(wooden_house.id)
    assert wooden_house.door is None

