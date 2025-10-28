import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import init_beanie


@pytest.mark.asyncio
async def test_do_nothing_rule_default():
    from beanie import Document, Link, ReferenceDeleteRules

    class Door(Document):
        height: int = 2

    class WoodenHouse(Document):
        name: str = "Wooden House"
        door: Link[Door]

    class MultiStoriedHouse(Document):
        name: str = "Multistoried House"
        doors: list[Link[Door]]

    client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")

    await init_beanie(
        client.db_name,
        document_models=[Door, WoodenHouse, MultiStoriedHouse]
    )

    door1 = await Door().insert()
    door_id = door1.id
    wooden_house = await WoodenHouse(door=door1).insert()
    await door1.delete()

    wooden_house = await WoodenHouse.get(wooden_house.id, fetch_links=True)
    assert wooden_house
    assert isinstance(wooden_house.door, Link)  # Object appears as link - since the actual entry is deleted
    assert wooden_house.door.ref.id == door_id

    door2 = await Door().insert()
    door3 = await Door().insert()
    multistoried_house = await MultiStoriedHouse(doors=[door3, door2]).insert()
    await door2.delete()

    multistoried_house = await MultiStoriedHouse.get(multistoried_house.id)
    assert multistoried_house.doors
    assert len(multistoried_house.doors) == 2
