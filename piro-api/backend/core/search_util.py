import json
from typing import Any
from core.exception_util import PIROException


def filter_str_object(str_input: str) -> str:
    """Convert a string containing JSON into a Solr query string."""
    obj = json.loads(str_input)
    return filter_generator(obj)


def filter_generator(json_input: Any) -> str:
    """Convert advanced search parameters (in JSON form) into a query string appropriate for Solr."""

    if (
        "field" in json_input.keys()
        and "operator" in json_input.keys()
        and "value" in json_input.keys()
    ):
        # process a single rule

        filter_item = ""
        field = json_input["field"].lower()
        value = json_input["value"]

        if value is None or value == "":
            raise PIROException(f"{field} {json_input['operator']} is empty")

        if field == "collectiondate":
            value = f"{value}T00:00:00Z"

        if json_input["operator"] == "contains":
            filter_item = f'{field}: "{value}"'
        elif json_input["operator"] == "not":
            filter_item = f'-{field}: "{value}"'
        elif json_input["operator"] == "=":
            filter_item = f'{field}: "{value}"'
        elif json_input["operator"] == "!=":
            filter_item = f'-{field}: "{value}"'
        elif json_input["operator"] == ">=":
            filter_item = f"{field}: [{value} TO *]"
        elif json_input["operator"] == "=<":
            filter_item = f"{field}: [* TO {value}]"
        elif json_input["operator"] == "in":
            filter_val_in = ", ".join(f'"{str(y)}"' for y in value)
            filter_item = f"{field}:({filter_val_in})"
        elif json_input["operator"] == "not in":
            filter_val_in = ", ".join(f'"{str(y)}"' for y in value)
            filter_item = f"-{field}:({filter_val_in})"
        return filter_item

    elif "field" in json_input.keys() and "operator" in json_input.keys():
        # if the 'value' key isn't present for a rule
        raise PIROException(
            f"{json_input['field']} {json_input['operator']} is empty"
        )

    elif "rules" in json_input.keys():
        # recursively process a set of rules
        condition: str = json_input["condition"].upper()
        filter: str = ""

        if len(json_input["rules"]) == 0:
            raise PIROException("Ruleset is empty")

        for item in json_input["rules"]:
            if filter == "":
                filter = filter_generator(item)
            else:
                filter = f"{filter} {condition} {filter_generator(item)}"

        return f"({filter})"
