from .delete import delete_record
from .write import insert_into_table
from .update import update_model
from .read import get_data_from_table

__all__ = [
    "delete_record",
    "insert_into_table",
    "update_model",
    "get_data_from_table",
]
