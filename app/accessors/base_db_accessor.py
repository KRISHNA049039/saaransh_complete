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
        query = self.apply_filters_and_sort(query, filters, sort)

        result = await session.execute(query)
        return result.scalars().all()

    def apply_filters_and_sort(
        self,
        query,
        filters: Optional[BaseModel],
        sort: Optional[SortQuery],
    ):
        query = self._apply_scd2_filter(query, filters)
        query = self._apply_filters(query, filters)
        query = self._apply_sort(query, sort)
        return query

    def _apply_scd2_filter(self, query, filters):
        if getattr(self.model, "__scd2__", False):
            if filters and getattr(filters, "effective_only", True):
                eff_to = getattr(self.model, "effective_to", None)
                if eff_to is not None:
                    query = query.where(eff_to.is_(None))

        return query

    def _apply_filters(self, query, filters):
        if not filters:
            return query

        for key, value in filters.model_dump(exclude_none=True).items():
            if key == "effective_only":
                continue

            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)

        return query

    def _apply_sort(self, query, sort):
        if not sort or not sort.sorts:
            return query

        orders = []
        for rule in sort.sorts:
            if hasattr(self.model, rule.field):
                col = getattr(self.model, rule.field)
                order = desc(col) if rule.direction == SortDirection.DESC else asc(col)

                if rule.nulls == NullsPosition.FIRST:
                    order = nullsfirst(order)
                elif rule.nulls == NullsPosition.LAST:
                    order = nullslast(order)

                orders.append(order)

        if orders:
            query = query.order_by(*orders)

        return query
