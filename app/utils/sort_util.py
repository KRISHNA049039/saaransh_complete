from enum import Enum
from typing import List, Optional
from fastapi import Query
from pydantic import BaseModel, field_validator


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class NullsPosition(str, Enum):
    FIRST = "nulls_first"
    LAST = "nulls_last"


class SortRule(BaseModel):
    field: str
    direction: SortDirection = SortDirection.ASC
    nulls: Optional[NullsPosition] = None

    @field_validator("field")
    def normalize_field(cls, v):
        return v.strip()

    @classmethod
    def parse_from_str(cls, raw: str) -> "SortRule":
        """
        Accepted formats:
            created_by
            -created_by
            created_by:asc
            created_by:desc
            created_by:desc,nulls_last
            -created_by,nulls_first
        """
        nulls = None

        if "," in raw:
            main, *flags = raw.split(",")
            raw = main
            for f in flags:
                f = f.strip().lower()
                if f == "nulls_first":
                    nulls = NullsPosition.FIRST
                elif f == "nulls_last":
                    nulls = NullsPosition.LAST

        # Handle `-field` syntax
        direction = SortDirection.ASC
        if raw.startswith("-"):
            direction = SortDirection.DESC
            raw = raw[1:]

        # Handle `field:direction` syntax
        if ":" in raw:
            field, dir_raw = raw.split(":")
            raw = field.strip()
            direction = SortDirection(dir_raw.strip().lower())

        return cls(field=raw, direction=direction, nulls=nulls)
    
    


class SortQuery(BaseModel):
    sorts: List[SortRule] = []


def parse_sort_query(
    sort: List[str] = Query(
        default=None,
        description=(
            "Sorting format: field, -field, field:asc, field:desc, "
            "field:desc,nulls_last. "
            "Multiple `sort` parameters allowed."
        )
    )
) -> SortQuery:
    if not sort:
        return SortQuery(sorts=[])

    rules = [SortRule.parse_from_str(s) for s in sort]
    return SortQuery(sorts=rules)

def sort_by(*rules: str) -> SortQuery:
    """
        sort_by("-created_by")
        sort_by("created_by:desc", "id:asc")
        sort_by("id:asc,nulls_last")
    """
    return SortQuery(sorts=[SortRule.parse_from_str(r) for r in rules])