# Tests for ReferenceDeleteRules on Link fields

from typing import Annotated, Optional

import pytest

from beanie import (
    BackLink,
    Document,
    Link,
    ReferenceDeleteRules,
    init_beanie,
)
from beanie.exceptions import DeleteDeniedError, DocumentNotFound
from beanie.odm.utils.pydantic import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from pydantic import Field
else:
    from pydantic.fields import Field


async def test_reference_delete_rules_on_delete(db):
    """Test that CASCADE, SET_NULL, DENY, DO_NOTHING and PULL_FROM_LIST
    work as expected when deleting a referenced document."""


    class DoorRD(Document):
        height: int = 1

    class WoodenHouseRD(Document):
        # Cascade delete house when door is deleted
        door: Annotated[Link[DoorRD], ReferenceDeleteRules.CASCADE]

    class GlassHouseRD(Document):
        # Do nothing when door is deleted
        door: Annotated[Link[DoorRD], ReferenceDeleteRules.DO_NOTHING]

    class MultiStoriedHouseRD(Document):
        # Pull door from list when door is deleted
        doors: Annotated[list[Link[DoorRD]], ReferenceDeleteRules.PULL_FROM_LIST]

    class NullableHouseRD(Document):
        # Set null on optional link when door is deleted
        door: Annotated[Optional[Link[DoorRD]], ReferenceDeleteRules.SET_NULL]

    await init_beanie(
        database=db,
        document_models=[
            DoorRD,
            WoodenHouseRD,
            GlassHouseRD,
            MultiStoriedHouseRD,
            NullableHouseRD,
        ],
    )

    door = await DoorRD().insert()
    wooden = await WoodenHouseRD(door=door).insert()
    glass = await GlassHouseRD(door=door).insert()
    multi = await MultiStoriedHouseRD(doors=[door]).insert()
    nullable = await NullableHouseRD(door=door).insert()

    # Delete the door, apply reference delete rules
    await door.delete()
    # WoodenHouseRD should have been deleted via CASCADE
    with pytest.raises(DocumentNotFound):
        await wooden.sync()

    # GlassHouseRD remains, still contains a reference to the deleted door.
    # Depending on whether the link was assigned a Document at insert time,
    # the `door` field here may be a Document instance or a Link.
    await glass.sync()

    # Ensure the door is still pointing at the same id, even though the doc was deleted
    if isinstance(glass.door, Link):
        assert glass.door.ref.id == door.id
    else:
        assert glass.door.id == door.id

    # MultiStoriedHouseRD should have had the door pulled from list
    await multi.sync()
    assert multi.doors == []

    # NullableHouseRD should have had door set to None
    await nullable.sync()
    assert nullable.door is None


async def test_reference_delete_rules_on_query_delete(db):
    """Verify delete rules also apply when removing documents via query API."""


    class DoorQuery(Document):
        height: int = 1

    class WoodenHouseQuery(Document):
        door: Annotated[Link[DoorQuery], ReferenceDeleteRules.CASCADE]

    class GlassHouseQuery(Document):
        door: Annotated[Link[DoorQuery], ReferenceDeleteRules.DO_NOTHING]

    class MultiStoriedHouseQuery(Document):
        doors: Annotated[
            list[Link[DoorQuery]],
            ReferenceDeleteRules.PULL_FROM_LIST,
        ]

    class NullableHouseQuery(Document):
        door: Annotated[Optional[Link[DoorQuery]], ReferenceDeleteRules.SET_NULL]

    await init_beanie(
        database=db,
        document_models=[
            DoorQuery,
            WoodenHouseQuery,
            GlassHouseQuery,
            MultiStoriedHouseQuery,
            NullableHouseQuery,
        ],
    )

    door = await DoorQuery().insert()
    wooden = await WoodenHouseQuery(door=door).insert()
    glass = await GlassHouseQuery(door=door).insert()
    multi = await MultiStoriedHouseQuery(doors=[door]).insert()
    nullable = await NullableHouseQuery(door=door).insert()

    await DoorQuery.find({"_id": door.id}).delete(comment="cascade-test")

    with pytest.raises(DocumentNotFound):
        await wooden.sync()

    await glass.sync()

    if isinstance(glass.door, Link):
        assert glass.door.ref.id == door.id
    else:
        assert glass.door.id == door.id

    await multi.sync()
    assert multi.doors == []

    await nullable.sync()
    assert nullable.door is None


async def test_reference_delete_rules_deny(db):
    """Test that DENY prevents deletion when references exist."""


    class DoorDeny(Document):
        pass

    class HouseDeny(Document):
        door: Annotated[Link[DoorDeny], ReferenceDeleteRules.DENY]

    await init_beanie(database=db, document_models=[DoorDeny, HouseDeny])
    door = await DoorDeny().insert()
    _ = await HouseDeny(door=door).insert()
    with pytest.raises(DeleteDeniedError):
        await door.delete()


async def test_invalid_reference_delete_rule_configuration(db):
    """Ensure invalid configurations of ReferenceDeleteRules raise errors."""

    class Dummy(Document):
        ...

    # SET_NULL on a non-optional link
    with pytest.raises(ValueError):
        class HouseInvalid(Document):
            door: Annotated[Link[Dummy], ReferenceDeleteRules.SET_NULL]

        await init_beanie(database=db, document_models=[Dummy, HouseInvalid])

    # PULL_FROM_LIST on a direct link
    with pytest.raises(ValueError):
        class HouseInvalid2(Document):
            door: Annotated[Link[Dummy], ReferenceDeleteRules.PULL_FROM_LIST]

        await init_beanie(database=db, document_models=[Dummy, HouseInvalid2])

    # CASCADE on a list link
    with pytest.raises(ValueError):
        class HouseInvalid3(Document):
            doors: Annotated[list[Link[Dummy]], ReferenceDeleteRules.CASCADE]

        await init_beanie(database=db, document_models=[Dummy, HouseInvalid3])

    # ReferenceDeleteRules specified on a BackLink field
    with pytest.raises(ValueError):
        class HouseInvalid4(Document):
            window: Annotated[Link[Dummy], ReferenceDeleteRules.CASCADE]

        if IS_PYDANTIC_V2:
            class BackDeny(Document):
                houses: Annotated[
                    list[BackLink[HouseInvalid4]], ReferenceDeleteRules.DENY
                ] = Field(json_schema_extra={"original_field": "window"})
        else:
            class BackDeny(Document):
                houses: Annotated[
                    list[BackLink[HouseInvalid4]], ReferenceDeleteRules.DENY
                ] = Field(original_field="window")

        await init_beanie(
            database=db, document_models=[Dummy, HouseInvalid4, BackDeny]
        )

    with pytest.raises(ValueError):
        class HouseInvalid5(Document):
            window: Annotated[Link[Dummy], ReferenceDeleteRules.CASCADE]

        if IS_PYDANTIC_V2:
            class BackDoNothing(Document):
                houses: Annotated[
                    list[BackLink[HouseInvalid5]], ReferenceDeleteRules.DO_NOTHING
                ] = Field(json_schema_extra={"original_field": "window"})
        else:
            class BackDoNothing(Document):
                houses: Annotated[
                    list[BackLink[HouseInvalid5]], ReferenceDeleteRules.DO_NOTHING
                ] = Field(original_field="window")

        await init_beanie(
            database=db, document_models=[Dummy, HouseInvalid5, BackDoNothing]
        )


async def test_reference_delete_rules_apply_to_subclasses(db):
    """Delete rules should respect subclass instances referenced via base types."""

    class BaseDoor(Document):
        height: int = 1

    class FancyDoor(BaseDoor):
        color: str = "red"

    class House(Document):
        door: Annotated[Link[BaseDoor], ReferenceDeleteRules.CASCADE]

    await init_beanie(
        database=db,
        document_models=[BaseDoor, FancyDoor, House],
    )

    fancy = await FancyDoor().insert()
    house = await House(door=fancy).insert()

    await fancy.delete()

    with pytest.raises(DocumentNotFound):
        await house.sync()


async def test_cascade_delete_handles_cycles(db):
    """Ensure cascading deletes terminate when references form a cycle."""

    class NodeA(Document):
        other: Annotated[
            Optional[Link["NodeB"]],
            ReferenceDeleteRules.CASCADE,
        ] = None

    class NodeB(Document):
        other: Annotated[
            Optional[Link[NodeA]],
            ReferenceDeleteRules.CASCADE,
        ] = None

    if IS_PYDANTIC_V2:
        NodeA.model_rebuild()
        NodeB.model_rebuild()
    else:
        NodeA.update_forward_refs()
        NodeB.update_forward_refs()

    await init_beanie(database=db, document_models=[NodeA, NodeB])

    node_a = await NodeA().insert()
    node_b = await NodeB(other=node_a).insert()

    node_a.other = node_b
    await node_a.save()

    await node_a.delete()

    assert await NodeA.get(node_a.id) is None
    assert await NodeB.get(node_b.id) is None
