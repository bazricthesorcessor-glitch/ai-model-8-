"""Quality checks for semantic extraction results."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type


class WebObserver:
    """Validate extraction completeness and schema integrity."""

    def assess(
        self,
        payload: Any,
        schema: Optional[Type[Any]] = None,
    ) -> Dict[str, Any]:
        issues = []
        quality = 1.0

        if payload is None:
            issues.append("empty_payload")
            quality = 0.0
        elif isinstance(payload, dict):
            if not payload:
                issues.append("empty_mapping")
                quality -= 0.6
            text_fields = [
                value for value in payload.values()
                if isinstance(value, str) and value.strip()
            ]
            if not text_fields:
                issues.append("no_text_fields")
                quality -= 0.3
        elif hasattr(payload, "model_dump"):
            model_dump = payload.model_dump()
            if not any(isinstance(value, str) and value.strip() for value in model_dump.values()):
                issues.append("schema_has_no_populated_text_fields")
                quality -= 0.3

        if schema is not None and payload is not None:
            try:
                if hasattr(schema, "model_validate"):
                    schema.model_validate(
                        payload if isinstance(payload, dict) else payload.model_dump()
                    )
            except Exception as exc:
                issues.append(f"schema_validation_failed:{exc}")
                quality -= 0.5

        quality = max(0.0, min(1.0, quality))
        return {
            "success": quality >= 0.5 and not any(issue.startswith("schema_validation_failed") for issue in issues),
            "quality_score": quality,
            "issues": issues,
        }
