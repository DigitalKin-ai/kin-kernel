"""
Test model generation
"""

from typing import Any, Dict
from pydantic import BaseModel, create_model
from pydantic.json_schema import JsonSchemaValue


json_schema = {
    "description": "Input data for the cron job",
    "type": "object",
    "properties": {
        "test": {
            "description": "This is a test 1 ",
            "allOf": [{"$ref": "#/$defs/TestObject"}],
        }
    },
    "$defs": {
        "TestObject": {
            "description": "Test object",
            "type": "object",
            "properties": {
                "message": {
                    "description": "Message of the test",
                    "type": "string",
                    "title": "Message",
                },
                "real_test": {"$ref": "#/$defs/RealTest"},
            },
            "title": "TestObject",
            "required": ["real_test", "message"],
        },
        "RealTest": {
            "description": "Real test",
            "type": "object",
            "properties": {
                "success": {
                    "description": "does the test succeed?",
                    "type": "boolean",
                    "title": "Success",
                }
            },
            "title": "RealTest",
            "required": ["success"],
        },
    },
    "title": "CronFibonacciInput",
    "required": ["test"],
}


# Original model
class User(BaseModel):
    id: int
    name: str
    is_active: bool
    score: float


def create_model_from_schema(schema: JsonSchemaValue, model_name: str) -> type[Any]:
    """
    Test model generation
    """
    fields: Dict[str, tuple[type, Any]] = {}

    for field_name, field_schema in schema.get("properties", {}).items():
        field_type = field_schema.get("type")
        print(field_name, field_type)
        if field_type == "string":
            fields[field_name] = (str, ...)
            print(field_schema.get("description"))
        elif field_type == "integer":
            fields[field_name] = (int, ...)
        elif field_type == "number":
            fields[field_name] = (float, ...)
        elif field_type == "boolean":
            fields[field_name] = (bool, ...)
        else:
            fields[field_name] = (Any, ...)

    return create_model(model_name, **fields)


if __name__ == "__main__":
    # Extract JSON schema
    user_schema = User.model_json_schema()
    print("user_schema", user_schema)
    print("-" * 50)
    print("json_schema", json_schema)
    print("-" * 50)
    # Create dynamic model
    DynamicUser = create_model_from_schema(json_schema, "DynamicUser")
    print(DynamicUser.model_json_schema())
