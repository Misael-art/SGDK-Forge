"""Small dependency-free JSON Schema gate for versioned forge-art documents."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class SchemaError(ValueError):
    pass


def load_schema(name: str) -> dict[str, Any]:
    return json.loads((Path(__file__).with_name("schemas") / f"{name}.schema.json").read_text(encoding="utf-8"))


def validate(instance: Any, schema: dict[str, Any], location: str = "$") -> None:
    if "const" in schema and instance != schema["const"]:
        raise SchemaError(f"{location}: expected const {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaError(f"{location}: value {instance!r} is not allowed")
    typ = schema.get("type")
    if typ == "object" and not isinstance(instance, dict):
        raise SchemaError(f"{location}: expected object")
    if isinstance(instance, dict) and (typ == "object" or "properties" in schema or "required" in schema):
        missing = sorted(set(schema.get("required", [])) - set(instance))
        if missing: raise SchemaError(f"{location}: missing required {missing}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = sorted(set(instance) - set(properties))
            if unknown: raise SchemaError(f"{location}: unknown properties {unknown}")
        for key, value in instance.items():
            if key in properties: validate(value, properties[key], f"{location}.{key}")
    elif typ == "array":
        if not isinstance(instance, list): raise SchemaError(f"{location}: expected array")
        if "minItems" in schema and len(instance) < schema["minItems"]: raise SchemaError(f"{location}: too few items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]: raise SchemaError(f"{location}: too many items")
        if "items" in schema:
            for index, value in enumerate(instance): validate(value, schema["items"], f"{location}[{index}]")
    elif typ == "string":
        if not isinstance(instance, str): raise SchemaError(f"{location}: expected string")
        if "minLength" in schema and len(instance) < schema["minLength"]: raise SchemaError(f"{location}: string shorter than minimum")
        if "maxLength" in schema and len(instance) > schema["maxLength"]: raise SchemaError(f"{location}: string longer than maximum")
        if "pattern" in schema and re.fullmatch(schema["pattern"], instance) is None: raise SchemaError(f"{location}: string violates portable contract")
    elif typ == "integer":
        if not isinstance(instance, int) or isinstance(instance, bool): raise SchemaError(f"{location}: expected integer")
        if "minimum" in schema and instance < schema["minimum"]: raise SchemaError(f"{location}: below minimum")
        if "maximum" in schema and instance > schema["maximum"]: raise SchemaError(f"{location}: above maximum")
        if "multipleOf" in schema and instance % schema["multipleOf"]: raise SchemaError(f"{location}: not a multiple")
    elif typ == "number":
        if not isinstance(instance, (int, float)) or isinstance(instance, bool): raise SchemaError(f"{location}: expected number")
        if "minimum" in schema and instance < schema["minimum"]: raise SchemaError(f"{location}: below minimum")
        if "maximum" in schema and instance > schema["maximum"]: raise SchemaError(f"{location}: above maximum")
    elif typ == "boolean" and not isinstance(instance, bool):
        raise SchemaError(f"{location}: expected boolean")
    for branch in schema.get("allOf", []):
        if "if" not in branch:
            validate(instance, branch, location); continue
        try: validate(instance, branch["if"], location)
        except SchemaError:
            if "else" in branch: validate(instance, branch["else"], location)
        else:
            if "then" in branch: validate(instance, branch["then"], location)
    if "not" in schema:
        try: validate(instance, schema["not"], location)
        except SchemaError: pass
        else: raise SchemaError(f"{location}: forbidden schema combination")


def validate_named(instance: Any, schema_name: str) -> None:
    validate(instance, load_schema(schema_name))
