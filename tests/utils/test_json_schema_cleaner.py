# pylint: disable-all
import json
import pytest
from kinkernel.utils.json_schema_cleaner import replace_refs_with_defs


def test_replace_refs_with_defs_without_refs():
    schema = {
        "title": "Person",
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name", "age"],
    }
    expected = {
        "name": "Person",
        "parameters": {
            "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            "required": ["name", "age"],
            "type": "object",
        },
    }
    assert replace_refs_with_defs(schema) == expected


def test_replace_refs_with_defs_with_refs():
    schema = {
        "$defs": {
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                },
                "required": ["street", "city"],
            }
        },
        "title": "Person",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "address": {"$ref": "#/$defs/address"},
        },
        "required": ["name", "age", "address"],
    }
    expected = {
        "name": "Person",
        "parameters": {
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                    },
                    "required": ["street", "city"],
                },
            },
            "required": ["name", "age", "address"],
            "type": "object",
        },
    }
    assert replace_refs_with_defs(schema) == expected


def test_replace_refs_with_defs_with_nested_refs():
    schema = {
        "$defs": {
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "country": {"$ref": "#/$defs/country"},
                },
                "required": ["street", "city", "country"],
            },
            "country": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "code": {"type": "string"}},
                "required": ["name", "code"],
            },
        },
        "title": "Person",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "address": {"$ref": "#/$defs/address"},
        },
        "required": ["name", "age", "address"],
    }

    expected = {
        "name": "Person",
        "parameters": {
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "country": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "code": {"type": "string"},
                            },
                            "required": ["name", "code"],
                        },
                    },
                    "required": ["street", "city", "country"],
                },
            },
            "required": ["name", "age", "address"],
            "type": "object",
        },
    }
    assert replace_refs_with_defs(schema) == expected


def test_replace_refs_with_defs_with_list():
    schema = {
        "$defs": {
            "item": {
                "type": "object",
                "properties": {"id": {"type": "integer"}, "value": {"type": "string"}},
                "required": ["id", "value"],
            }
        },
        "title": "ItemList",
        "type": "object",
        "properties": {"items": {"type": "array", "items": {"$ref": "#/$defs/item"}}},
        "required": ["items"],
    }
    expected = {
        "name": "ItemList",
        "parameters": {
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "value": {"type": "string"},
                        },
                        "required": ["id", "value"],
                    },
                }
            },
            "required": ["items"],
            "type": "object",
        },
    }
    assert replace_refs_with_defs(schema) == expected


def test_replace_refs_with_defs_with_missing_defs():
    schema = {
        "title": "Person",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "address": {"$ref": "#/$defs/address"},
        },
        "required": ["name", "age", "address"],
    }

    with pytest.raises(KeyError):
        replace_refs_with_defs(schema)
