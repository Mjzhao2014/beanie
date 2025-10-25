from typing import TYPE_CHECKING, Any, Dict, Generator, Mapping, Optional, Type

from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo import DeleteMany as DeleteManyPyMongo
from pymongo import DeleteOne as DeleteOnePyMongo
from pymongo.results import DeleteResult

from beanie.odm.bulk import BulkWriter
from beanie.odm.interfaces.clone import CloneInterface
from beanie.odm.interfaces.session import SessionMethods

if TYPE_CHECKING:
    from beanie.odm.documents import DocType


class DeleteQuery(SessionMethods, CloneInterface):
    """
    Deletion Query
    """

    def __init__(
        self,
        document_model: Type["DocType"],
        find_query: Mapping[str, Any],
        bulk_writer: Optional[BulkWriter] = None,
        **pymongo_kwargs: Any,
    ):
        self.document_model = document_model
        self.find_query = find_query
        self.session: Optional[AsyncIOMotorClientSession] = None
        self.bulk_writer = bulk_writer
        self.pymongo_kwargs: Dict[str, Any] = dict(pymongo_kwargs)
        self._reference_rules_applied = self.pymongo_kwargs.pop(
            "_reference_rules_applied", False
        )


class DeleteMany(DeleteQuery):
    def __await__(
        self,
    ) -> Generator[DeleteResult, None, Optional[DeleteResult]]:
        """
        Run the query
        :return:
        """
        if not self._reference_rules_applied:
            documents_query = self.document_model.find_many(
                self.find_query,
                session=self.session,
                ignore_cache=True,
                **self.pymongo_kwargs,
            )
            documents = yield from documents_query.to_list().__await__()
            for document in documents:
                yield from document._apply_reference_delete_rules(
                    session=self.session,
                    bulk_writer=self.bulk_writer,
                ).__await__()
        if self.bulk_writer is None:
            return (
                yield from self.document_model.get_motor_collection()
                .delete_many(
                    self.find_query,
                    session=self.session,
                    **self.pymongo_kwargs,
                )
                .__await__()
            )
        else:
            self.bulk_writer.add_operation(
                self.document_model,
                DeleteManyPyMongo(self.find_query, **self.pymongo_kwargs),
            )
            return None


class DeleteOne(DeleteQuery):
    def __await__(
        self,
    ) -> Generator[DeleteResult, None, Optional[DeleteResult]]:
        """
        Run the query
        :return:
        """
        if not self._reference_rules_applied:
            document = yield from self.document_model.find_one(
                self.find_query,
                session=self.session,
                ignore_cache=True,
                **self.pymongo_kwargs,
            ).__await__()
            if document is not None:
                yield from document._apply_reference_delete_rules(
                    session=self.session,
                    bulk_writer=self.bulk_writer,
                ).__await__()
        if self.bulk_writer is None:
            return (
                yield from self.document_model.get_motor_collection()
                .delete_one(
                    self.find_query,
                    session=self.session,
                    **self.pymongo_kwargs,
                )
                .__await__()
            )
        else:
            self.bulk_writer.add_operation(
                self.document_model,
                DeleteOnePyMongo(self.find_query),
                **self.pymongo_kwargs,
            )
            return None
