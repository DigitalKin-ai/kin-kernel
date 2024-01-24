"""
This module provides a utility to clean JSON schemas by replacing `$ref` references with their actual definitions.
"""
import json


def replace_refs_with_defs(schema: dict) -> dict:
    """
    Replaces all `$ref` references in a JSON schema with their corresponding definitions from the `$defs` section.

    :param schema: The JSON schema containing `$ref` references and a `$defs` section.
    :type schema: dict
    :return: The JSON schema with all `$ref` references replaced by their actual definitions.
    :rtype: dict
    """

    def resolve_ref(ref: str, defs: dict) -> dict:
        """
        Resolves a `$ref` reference using the definitions provided.

        :param ref: The reference string to resolve.
        :type ref: str
        :param defs: A dictionary of definitions to resolve the reference against.
        :type defs: dict
        :return: The resolved schema for the given reference.
        :rtype: dict
        """
        # Remove the #/ and split by '/'
        path = ref.replace("#/$defs/", "").split("/")
        ref_schema = defs
        for key in path:
            ref_schema = ref_schema[key]
        return ref_schema

    def replace_refs(obj: dict, defs: dict) -> dict:
        """
        Recursively replaces `$ref` references within an object (dictionary or list) with their definitions.

        :param obj: The object (dictionary or list) to process.
        :type obj: dict | list
        :param defs: A dictionary of definitions to resolve references against.
        :type defs: dict
        :return: The object with all `$ref` references replaced by their actual definitions.
        :rtype: dict | list
        """
        if isinstance(obj, dict):
            if "$ref" in obj:
                # Replace the $ref with the actual definition
                ref = obj.pop("$ref")
                ref_schema = resolve_ref(ref, defs)
                if "$ref" in json.dumps(ref_schema):
                    replace_refs(ref_schema, defs)
                obj.update(ref_schema)
            else:
                # Recursively replace $ref in each dictionary
                for key, value in obj.items():
                    obj[key] = replace_refs(value, defs)
        elif isinstance(obj, list):
            # Recursively replace $ref in each list item
            obj = [replace_refs(item, defs) for item in obj]
        return obj

    if "$defs" not in schema and "$ref" in json.dumps(schema):
        raise KeyError("Schema does not have any defs however it contains some ref")

    if "$defs" in schema:
        defs = schema.pop("$defs")
        schema = replace_refs(schema, defs)
    schema["parameters"] = {
        "properties": schema["properties"],
        "required": schema["required"],
        "type": schema["type"],
    }
    schema["name"] = schema["title"]
    del schema["title"]
    del schema["properties"]
    del schema["required"]
    del schema["type"]
    return schema


# Example usage:
# if __name__ == "__main__":
#     example_schema = {
#         "$defs": {
#             "address": {
#                 "type": "object",
#                 "properties": {
#                     "street": {"type": "string"},
#                     "city": {"type": "string"}
#                 },
#                 "required": ["street", "city"]
#             }
#         },
#         "title": "Person",
#         "type": "object",
#         "properties": {
#             "name": {"type": "string"},
#             "age": {"type": "integer"},
#             "address": {"$ref": "#/$defs/address"}
#         },
#         "required": ["name", "age", "address"]
#     }
#     cleaned_schema = replace_refs_with_defs(example_schema)
#     print(cleaned_schema)
