"""Schema registry and validation helpers for semantic extraction."""

from __future__ import annotations

from typing import Any, Optional, Type

from pydantic import BaseModel, ValidationError

from schemas import SCHEMA_REGISTRY


class SchemaService:
    """Resolve and validate extraction schemas."""

    def resolve(self, schema: Optional[Any]) -> Optional[Type[BaseModel]]:
        if schema is None:
            return None
        if isinstance(schema, str):
            resolved = SCHEMA_REGISTRY.get(schema)
            if resolved is None:
                raise ValueError(f"Unknown schema '{schema}'. Available: {sorted(SCHEMA_REGISTRY)}")
            return resolved
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            return schema
        raise TypeError("schema must be None, a schema name, or a Pydantic BaseModel class")

    def validate(self, schema: Optional[Any], payload: Any) -> Any:
        resolved = self.resolve(schema)
        if resolved is None:
            return payload
        if isinstance(payload, resolved):
            return payload
        return resolved.model_validate(payload)

    def dump(self, payload: Any) -> Any:
        if hasattr(payload, "model_dump"):
            return payload.model_dump()
        return payload

    def json_schema(self, schema: Optional[Any]) -> Optional[dict]:
        resolved = self.resolve(schema)
        if resolved is None:
            return None
        return resolved.model_json_schema()

    def schema_name(self, schema: Optional[Any]) -> Optional[str]:
        resolved = self.resolve(schema)
        if resolved is None:
            return None
        return resolved.__name__

