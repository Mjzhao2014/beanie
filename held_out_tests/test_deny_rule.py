from typing import Annotated, Optional

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import init_beanie


@pytest.mark.asyncio
async def test_deny_rule():
    from typing import Annotated

    from beanie import Document, Link, ReferenceDeleteRules
    from beanie.exceptions import DeleteDeniedError

    class Door(Document):
        height: int = 2

    class MultiStoriedHouse(Document):
        name: str = "Multistoried House"
        doors: Annotated[list[Link[Door]], ReferenceDeleteRules.PULL_FROM_LIST]

    class WoodenHouse(Document):
        name: str = "Wooden House"
        door: Annotated[Link[Door], ReferenceDeleteRules.DENY]

    client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")

    await init_beanie(
        client.db_name,
        document_models=[Door, WoodenHouse, MultiStoriedHouse]
    )

    door1 = await Door().insert()

    wooden_house = await WoodenHouse(door=door1).insert()

    with pytest.raises(DeleteDeniedError):
        await door1.delete()

    wooden_house = await WoodenHouse.get(wooden_house.id, fetch_links=True)
    assert isinstance(wooden_house.door, Door) # The object is fetched if not-deleted
    assert wooden_house.door.id == door1.id