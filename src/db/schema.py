from typing import Dict, Optional, Set, Type

from pydantic import BaseModel, create_model, Field
from sqlalchemy.orm import InstrumentedAttribute

from src.db import Base


def sqlalchemy_table_to_pydantic(
    model: Type[Base],
    name: str = "DynamicSchema",
    include: Optional[Set[str]] = None,
    exclude: Optional[Set[str]] = None,
    rename: Optional[Dict[str, str]] = {},
    extra: Optional[Set[InstrumentedAttribute]] = None,
    make_optional: bool = False,
) -> Type[BaseModel]:
    fields = {}

    for column in model.__table__.columns:
        col_name = column.name

        if include and col_name not in include:
            continue
        if exclude and col_name in exclude:
            continue
        if col_name in rename.keys():
            col_name = rename.get(col_name)

        try:
            py_type = column.type.python_type
        except NotImplementedError:
            py_type = str

        default = None if (column.nullable or make_optional) else ...
        description = column.info.get("description") if column.info else None

        fields[col_name] = (py_type, Field(default, description=description))

    if extra:
        for attr in extra:
            _name: str = attr.key
            if _name in fields:
                continue
            if _name in rename.keys():
                _name = rename.get(_name)

            try:
                py_type = attr.property.columns[0].type.python_type
                nullable = attr.property.columns[0].nullable
            except Exception:
                py_type = str
                nullable = True

            default = None if (nullable or make_optional) else ...
            fields[_name] = (py_type, Field(default))

    return create_model(name, **fields)
