from typing import Annotated

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from beanie import Document, BackLink, Link, init_beanie
from pydantic import Field

@pytest.mark.asyncio
async def test_backlink_del_rule_error():
    from beanie import ReferenceDeleteRules
    with pytest.raises(Exception):
        class House(Document):
            name: str
            door: Link["Door"]

        class Door(Document):
            height: int = 2
            width: int = 1
            house: Annotated[BackLink[House], ReferenceDeleteRules.DENY] = Field(original_field="door")

        House.model_rebuild()

        client = AsyncIOMotorClient("mongodb://127.0.0.1:27017")

        await init_beanie(
            client.db_name,
            document_models=[House, Door]
        )
