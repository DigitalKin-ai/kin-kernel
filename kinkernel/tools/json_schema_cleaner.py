"""
TODO: sphinx docstring
"""


def replace_refs_with_defs(schema: dict) -> dict:
    """
    TODO: sphinx docstring
    """

    def resolve_ref(ref: str, defs: dict) -> dict:
        """
        TODO: sphinx docstring
        """
        # Remove the #/ and split by '/'
        path = ref.replace("#/$defs/", "").split("/")
        ref_schema = defs
        for key in path:
            ref_schema = ref_schema[key]
        return ref_schema

    def replace_refs(obj: dict, defs: dict) -> dict:
        """
        TODO: sphinx docstring
        """
        if isinstance(obj, dict):
            if "$ref" in obj:
                # Replace the $ref with the actual definition
                ref = obj.pop("$ref")
                ref_schema = resolve_ref(ref, defs)
                obj.update(ref_schema)
            else:
                # Recursively replace $ref in each dictionary
                for key, value in obj.items():
                    obj[key] = replace_refs(value, defs)
        elif isinstance(obj, list):
            # Recursively replace $ref in each list item
            obj = [replace_refs(item, defs) for item in obj]
        return obj

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
