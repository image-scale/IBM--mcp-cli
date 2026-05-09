"""Tool schema validation for MCP CLI.

Validates and fixes tool schemas for compatibility with LLM providers.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, cast

from mcpcli.tools.models import ValidationResult

logger = logging.getLogger(__name__)

UNSUPPORTED_FUNCTION_PROPS = ["title", "examples", "deprecated", "version", "tags", "summary"]
UNSUPPORTED_PARAM_PROPS = ["title", "examples", "deprecated"]


class ToolSchemaValidator:
    """Validates tool schemas for compatibility with different LLM providers."""

    @staticmethod
    def validate_openai_schema(tool_def: dict[str, Any]) -> ValidationResult:
        """Validate a tool definition against OpenAI's function calling schema.

        Args:
            tool_def: Tool definition dictionary.

        Returns:
            ValidationResult with validation status and any errors.
        """
        try:
            if "function" not in tool_def:
                return ValidationResult.failure(
                    "Tool definition missing 'function' property"
                )

            function = tool_def.get("function", {})
            if not isinstance(function, dict):
                return ValidationResult.failure("Function must be a dictionary")

            name = function.get("name", "")
            if not name or not isinstance(name, str):
                return ValidationResult.failure(
                    "Function name must be a non-empty string"
                )

            if not re.match(r"^[a-zA-Z0-9_-]+$", name):
                return ValidationResult.failure(
                    f"Function name '{name}' contains invalid characters. "
                    "Only a-z, A-Z, 0-9, _, - allowed"
                )

            for prop in UNSUPPORTED_FUNCTION_PROPS:
                if prop in function:
                    return ValidationResult.failure(
                        f"Function contains unsupported property '{prop}'"
                    )

            if "parameters" in function:
                parameters = function["parameters"]
                if not isinstance(parameters, dict):
                    return ValidationResult.failure("Parameters must be a dictionary")

                array_errors = ToolSchemaValidator._check_array_schemas(parameters)
                if array_errors:
                    return ValidationResult.failure(
                        f"Array schema issues: {'; '.join(array_errors)}"
                    )

            return ValidationResult.success()

        except Exception as e:
            return ValidationResult.failure(f"Validation error: {str(e)}")

    @staticmethod
    def _check_array_schemas(obj: Any, path: str = "") -> list[str]:
        """Recursively check for array schemas missing 'items' property.

        Args:
            obj: Schema object to check.
            path: Current path for error messages.

        Returns:
            List of error messages.
        """
        errors: list[str] = []

        if isinstance(obj, dict):
            if obj.get("type") == "array" and "items" not in obj:
                errors.append(
                    f"Array schema at {path or 'root'} missing 'items' property"
                )

            for schema_key in ["anyOf", "oneOf", "allOf"]:
                if schema_key in obj and isinstance(obj[schema_key], list):
                    for i, schema in enumerate(obj[schema_key]):
                        sub_path = (
                            f"{path}.{schema_key}[{i}]"
                            if path
                            else f"{schema_key}[{i}]"
                        )
                        errors.extend(
                            ToolSchemaValidator._check_array_schemas(schema, sub_path)
                        )

            for key, value in obj.items():
                if key not in ["anyOf", "oneOf", "allOf"]:
                    sub_path = f"{path}.{key}" if path else key
                    errors.extend(
                        ToolSchemaValidator._check_array_schemas(value, sub_path)
                    )

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                sub_path = f"{path}[{i}]" if path else f"[{i}]"
                errors.extend(ToolSchemaValidator._check_array_schemas(item, sub_path))

        return errors

    @staticmethod
    def fix_array_schemas(parameters: dict[str, Any]) -> dict[str, Any]:
        """Fix common array schema issues by adding default items.

        Args:
            parameters: Parameters schema to fix.

        Returns:
            Fixed parameters schema.
        """
        fixed = json.loads(json.dumps(parameters))
        ToolSchemaValidator._fix_array_schemas_recursive(fixed)
        return cast(dict[str, Any], fixed)

    @staticmethod
    def _fix_array_schemas_recursive(obj: Any) -> None:
        """Recursively fix array schemas in place.

        Args:
            obj: Schema object to fix.
        """
        if isinstance(obj, dict):
            if obj.get("type") == "array" and "items" not in obj:
                logger.debug(f"Fixing array schema without items: {obj}")
                obj["items"] = {"type": "string"}

            for schema_key in ["anyOf", "oneOf", "allOf"]:
                if schema_key in obj and isinstance(obj[schema_key], list):
                    for schema in obj[schema_key]:
                        ToolSchemaValidator._fix_array_schemas_recursive(schema)

            for value in obj.values():
                if isinstance(value, (dict, list)):
                    ToolSchemaValidator._fix_array_schemas_recursive(value)

        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    ToolSchemaValidator._fix_array_schemas_recursive(item)

    @staticmethod
    def fix_openai_compatibility(tool_def: dict[str, Any]) -> dict[str, Any]:
        """Fix OpenAI compatibility by removing unsupported properties.

        Args:
            tool_def: Tool definition to fix.

        Returns:
            Fixed tool definition.
        """
        fixed = json.loads(json.dumps(tool_def))

        if "function" in fixed and isinstance(fixed["function"], dict):
            function = fixed["function"]

            removed_props = []
            for prop in UNSUPPORTED_FUNCTION_PROPS:
                if prop in function:
                    removed_props.append(prop)
                    del function[prop]

            if removed_props:
                logger.debug(
                    f"Removed unsupported properties {removed_props} from "
                    f"function '{function.get('name', 'unknown')}'"
                )

            if "parameters" in function and isinstance(function["parameters"], dict):
                fixed["function"]["parameters"] = ToolSchemaValidator.fix_array_schemas(
                    function["parameters"]
                )

                param_removed = []
                for prop in UNSUPPORTED_PARAM_PROPS:
                    if prop in fixed["function"]["parameters"]:
                        param_removed.append(prop)
                        del fixed["function"]["parameters"][prop]

                if param_removed:
                    logger.debug(
                        f"Removed unsupported parameter properties {param_removed}"
                    )

        return cast(dict[str, Any], fixed)

    @staticmethod
    def validate_and_fix_tool(
        tool_def: dict[str, Any],
        provider: str = "openai",
    ) -> tuple[bool, dict[str, Any], str | None]:
        """Validate and fix a tool definition.

        First attempts to fix the tool, then validates the fixed version.

        Args:
            tool_def: Tool definition to validate and fix.
            provider: LLM provider name.

        Returns:
            Tuple of (is_valid, fixed_tool_def, error_message).
        """
        if provider != "openai":
            return True, tool_def, None

        try:
            fixed_tool = ToolSchemaValidator.fix_openai_compatibility(tool_def)
            validation = ToolSchemaValidator.validate_openai_schema(fixed_tool)
            return validation.is_valid, fixed_tool, validation.error_message

        except Exception as e:
            return False, tool_def, f"Error during fix/validation: {str(e)}"


__all__ = [
    "ToolSchemaValidator",
]
