"""
Convert a rowset to the json table schema
(http://www.dataprotocols.org/en/latest/json-table-schema.html)
"""

from messytables.headers import headers_guess
from messytables.types import (
    BoolType,
    DateType,
    DateUtilType,
    DecimalType,
    FloatType,
    IntegerType,
    StringType,
    type_guess,
)

MESSYTABLES_TO_JTS_MAPPING = {
    StringType: "string",
    IntegerType: "integer",
    FloatType: "number",
    DecimalType: "number",
    DateType: "date",
    DateUtilType: "date",
    BoolType: "boolean",
}


def celltype_as_string(celltype):
    return MESSYTABLES_TO_JTS_MAPPING[celltype.__class__]


class JSONTableSchema:
    """A simple JSON Table Schema representation."""

    def __init__(self):
        self._fields = []

    def add_field(self, field_id, label, field_type):
        self._fields.append(
            {
                "id": field_id,
                "label": label,
                "type": field_type,
            }
        )

    def as_dict(self):
        return {"fields": self._fields}


def rowset_as_jts(rowset, headers=None, types=None):
    """Create a json table schema from a rowset"""
    _, headers = headers_guess(rowset.sample)
    types = list(map(celltype_as_string, type_guess(rowset.sample)))

    return headers_and_typed_as_jts(headers, types)


def headers_and_typed_as_jts(headers, types):
    """Create a json table schema from headers and types as
    returned from :meth:`~messytables.headers.headers_guess`
    and :meth:`~messytables.types.type_guess`.
    """
    j = JSONTableSchema()

    for field_id, field_type in zip(headers, types):
        j.add_field(field_id=field_id, label=field_id, field_type=field_type)

    return j
