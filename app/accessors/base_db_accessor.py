from typing import Type, TypeVar, Generic, Optional, cast
from sqlalchemy import exists, select, asc, desc, nullsfirst, nullslast
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.models.orm.base import Base
from app.utils.sort_util import SortQuery, SortDirection, NullsPosition
from app.utils.scd2_protocol import SCD2Model
from app.utils.scd2_protocol import SCD2Filter

ModelType = TypeVar("ModelType", bound=Base)


class BaseDBAccessor(Generic[ModelType]):
    model: Type[ModelType]

    async def fetch(
        self,
        session: AsyncSession,
        filters: Optional[BaseModel] = None,
        sort: Optional[SortQuery] = None,
    ):
        query = select(self.model)

        # scd2 table check
        if getattr(self.model, "__scd2__", False):

            scd2_model = cast(SCD2Model, self.model)
            scd2_filter = cast(SCD2Filter, filters)

            if scd2_filter.effective_only:
                query = query.where(scd2_model.effective_to.is_(None))

        # Filtering
        if filters:
            for key, value in filters.model_dump(exclude_none=True).items():
                if key == "active_only":
                    continue
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)

        # Sorting
        if sort and sort.sorts:
            orders = []
            for rule in sort.sorts:
                if not hasattr(self.model, rule.field):
                    continue

                column = getattr(self.model, rule.field)
                order = (
                    desc(column)
                    if rule.direction == SortDirection.DESC
                    else asc(column)
                )

                if rule.nulls == NullsPosition.FIRST:
                    order = nullsfirst(order)
                elif rule.nulls == NullsPosition.LAST:
                    order = nullslast(order)

                orders.append(order)

            if orders:
                query = query.order_by(*orders)

        result = await session.execute(query)
        return result.scalars().all()
