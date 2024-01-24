"""
This package provides utils functions.

The `replace_refs_with_defs` function cleans a JSON schema by replacing `$ref` references with their actual definitions.

Functions:
    - replace_refs_with_defs(schema): Cleans a JSON schema by replacing `$ref` references with their actual definitions.
"""
from kinkernel.utils.json_schema_cleaner import replace_refs_with_defs

__all__ = ["replace_refs_with_defs"]
