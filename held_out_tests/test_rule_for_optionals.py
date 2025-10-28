from typing import Annotated, Optional

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import init_beanie

@pytest.mark.asyncio
async def test_rule_for_optionals():
    from typing import Annotated

    from beanie import Document, Link, ReferenceDeleteRules
    from beanie.exceptions import DeleteDeniedError

    class Door(Document):
        height: int = 2

    class WoodenHouse(Document):
        name: str = "Wooden House"
        door: Annotated[Optional[Link[Door]], ReferenceDeleteRules.DENY]

    class MultiStoriedHouse(Document):
        name: str = "Multistoried House"
        doors: Annotated[Optional[list[Link[Door]]], ReferenceDeleteRules.PULL_FROM_LIST]

    client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")

    await init_beanie(
        client.db_name,
        document_models=[Door, WoodenHouse, MultiStoriedHouse]
    )

    door1 = await Door().insert()
    door2 = await Door().insert()

    wooden_house = await WoodenHouse(door=door2).insert()

    multistoried_house = await MultiStoriedHouse(doors=[door1, door2]).insert()

    with pytest.raises(DeleteDeniedError):
        # Denied as it holds a reference in wooden_house - with DENY rule.
        await door2.delete()

    # This should execute successfully - pulling its entry in multistoried_house.doors
    await door1.delete()

    wooden_house = await WoodenHouse.get(wooden_house.id, fetch_links=True)
    assert wooden_house.door.id == door2.id

    multistoried_house = await MultiStoriedHouse.get(multistoried_house.id)

    assert multistoried_house
    assert len(multistoried_house.doors) == 1
    assert multistoried_house.doors[0].ref.id == door2.id
