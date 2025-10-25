from typing import Annotated

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import init_beanie

@pytest.mark.asyncio
async def test_do_nothing_rule_lists():
    from typing import Annotated

    from beanie import Document, Link, ReferenceDeleteRules

    class Door(Document):
        height: int = 2

    class MultiStoriedHouse(Document):
        name: str = "Multistoried House"
        doors: Annotated[list[Link[Door]], ReferenceDeleteRules.DO_NOTHING]


    client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")

    await init_beanie(
        client.db_name,
        document_models=[Door, MultiStoriedHouse]
    )

    door1 = await Door().insert()

    door2 = await Door().insert()

    multistoried_house = await MultiStoriedHouse(doors=[door1, door2]).insert()

    await door1.delete()

    multistoried_house = await MultiStoriedHouse.get(multistoried_house.id)

    assert multistoried_house.doors
    assert len(multistoried_house.doors) == 2