from typing import Annotated, Optional

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import init_beanie

@pytest.mark.asyncio
async def test_cascade_set_null_combination():
    from typing import Annotated

    from beanie import Document, Link, ReferenceDeleteRules

    class Door(Document):
        height: int = 2

    class WoodenHouse(Document):
        name: str = "Wooden House"
        door: Annotated[Link[Door], ReferenceDeleteRules.CASCADE]

    class TreeHouse(Document):
        name: str = "Tree House"
        door: Annotated[Optional[Link[Door]], ReferenceDeleteRules.SET_NULL] = None

    client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")

    await init_beanie(
        client.db_name,
        document_models=[Door, WoodenHouse, TreeHouse]
    )

    door1 = await Door().insert()
    wooden_house = await WoodenHouse(door=door1).insert()
    tree_house = await TreeHouse(door=door1).insert()

    await door1.delete()

    wooden_house = await WoodenHouse.get(wooden_house.id, fetch_links=True)
    assert wooden_house is None

    tree_house = await TreeHouse.get(tree_house.id, fetch_links=True)
    assert tree_house
    assert tree_house.door is None
