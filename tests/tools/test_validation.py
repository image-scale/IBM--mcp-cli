"""Tests for tool validation."""

from __future__ import annotations

import pytest

from mcpcli.tools.validation import ToolSchemaValidator


class TestValidateOpenaiSchema:
    """Tests for validate_openai_schema method."""

    def test_validate_valid_tool(self) -> None:
        """Validates a valid tool definition."""
        tool = {
            "type": "function",
            "function": {
                "name": "valid_tool",
                "description": "A valid tool",
                "parameters": {
                    "type": "object",
                    "properties": {"arg1": {"type": "string"}},
                },
            },
        }

        result = ToolSchemaValidator.validate_openai_schema(tool)
        assert result.is_valid is True
        assert result.error_message is None

    def test_validate_missing_function(self) -> None:
        """Fails when function property is missing."""
        tool = {"type": "function"}

        result = ToolSchemaValidator.validate_openai_schema(tool)
        assert result.is_valid is False
        assert "missing 'function' property" in result.error_message

    def test_validate_function_not_dict(self) -> None:
        """Fails when function is not a dictionary."""
        tool = {"type": "function", "function": "not a dict"}

        result = ToolSchemaValidator.validate_openai_schema(tool)
        assert result.is_valid is False
        assert "must be a dictionary" in result.error_message

    def test_validate_missing_name(self) -> None:
        """Fails when name is missing."""
        tool = {"type": "function", "function": {"description": "No name"}}

        result = ToolSchemaValidator.validate_openai_schema(tool)
        assert result.is_valid is False
        assert "name must be a non-empty string" in result.error_message

    def test_validate_empty_name(self) -> None:
        """Fails when name is empty."""
        tool = {"type": "function", "function": {"name": ""}}

        result = ToolSchemaValidator.validate_openai_schema(tool)
        assert result.is_valid is False
        assert "name must be a non-empty string" in result.error_message

    def test_validate_invalid_name_characters(self) -> None:
        """Fails when name contains invalid characters."""
        tool = {
            "type": "function",
            "function": {"name": "invalid@name", "description": "Test"},
        }

        result = ToolSchemaValidator.validate_openai_schema(tool)
        assert result.is_valid is False
        assert "contains invalid characters" in result.error_message

    @pytest.mark.parametrize(
        "name",
        ["valid_name", "ValidName", "valid-name", "valid123", "valid_name_123"],
    )
    def test_validate_valid_names(self, name: str) -> None:
        """Validates various valid names."""
        tool = {
            "type": "function",
            "function": {"name": name, "description": "Test"},
        }

        result = ToolSchemaValidator.validate_openai_schema(tool)
        assert result.is_valid is True
        assert result.error_message is None

    @pytest.mark.parametrize(
        "prop", ["title", "examples", "deprecated", "version", "tags"]
    )
    def test_validate_unsupported_properties(self, prop: str) -> None:
        """Fails when unsupported properties are present."""
        tool = {
            "type": "function",
            "function": {"name": "tool", "description": "Test", prop: "value"},
        }

        result = ToolSchemaValidator.validate_openai_schema(tool)
        assert result.is_valid is False
        assert f"unsupported property '{prop}'" in result.error_message

    def test_validate_parameters_not_dict(self) -> None:
        """Fails when parameters is not a dictionary."""
        tool = {
            "type": "function",
            "function": {"name": "tool", "description": "Test", "parameters": "string"},
        }

        result = ToolSchemaValidator.validate_openai_schema(tool)
        assert result.is_valid is False
        assert "Parameters must be a dictionary" in result.error_message

    def test_validate_array_without_items(self) -> None:
        """Fails when array is missing items."""
        tool = {
            "type": "function",
            "function": {
                "name": "tool",
                "description": "Test",
                "parameters": {
                    "type": "object",
                    "properties": {"arr": {"type": "array"}},
                },
            },
        }

        result = ToolSchemaValidator.validate_openai_schema(tool)
        assert result.is_valid is False
        assert "Array schema" in result.error_message
        assert "missing 'items'" in result.error_message


class TestCheckArraySchemas:
    """Tests for _check_array_schemas method."""

    def test_check_array_schemas_nested(self) -> None:
        """Finds nested array issues."""
        schema = {
            "type": "object",
            "properties": {
                "nested": {
                    "type": "object",
                    "properties": {"arr": {"type": "array"}},
                }
            },
        }

        errors = ToolSchemaValidator._check_array_schemas(schema)
        assert len(errors) > 0
        assert any("missing 'items'" in e for e in errors)

    def test_check_array_schemas_anyof(self) -> None:
        """Finds array issues in anyOf."""
        schema = {"anyOf": [{"type": "array"}, {"type": "string"}]}

        errors = ToolSchemaValidator._check_array_schemas(schema)
        assert len(errors) > 0

    def test_check_array_schemas_valid_array(self) -> None:
        """No errors for valid array."""
        schema = {
            "type": "object",
            "properties": {"arr": {"type": "array", "items": {"type": "string"}}},
        }

        errors = ToolSchemaValidator._check_array_schemas(schema)
        assert len(errors) == 0

    def test_check_array_schemas_with_list(self) -> None:
        """Handles list input."""
        obj = [{"type": "array"}, {"type": "string"}]

        errors = ToolSchemaValidator._check_array_schemas(obj)
        assert len(errors) > 0


class TestFixArraySchemas:
    """Tests for fix_array_schemas method."""

    def test_fix_array_schemas_simple(self) -> None:
        """Fixes simple array missing items."""
        parameters = {
            "type": "object",
            "properties": {"arr": {"type": "array"}},
        }

        fixed = ToolSchemaValidator.fix_array_schemas(parameters)

        assert fixed["properties"]["arr"]["items"] == {"type": "string"}

    def test_fix_array_schemas_nested(self) -> None:
        """Fixes nested array issues."""
        parameters = {
            "type": "object",
            "properties": {
                "nested": {
                    "type": "object",
                    "properties": {"arr": {"type": "array"}},
                }
            },
        }

        fixed = ToolSchemaValidator.fix_array_schemas(parameters)

        assert fixed["properties"]["nested"]["properties"]["arr"]["items"] == {
            "type": "string"
        }

    def test_fix_array_schemas_preserves_existing_items(self) -> None:
        """Preserves existing items property."""
        parameters = {
            "type": "object",
            "properties": {"arr": {"type": "array", "items": {"type": "number"}}},
        }

        fixed = ToolSchemaValidator.fix_array_schemas(parameters)

        assert fixed["properties"]["arr"]["items"]["type"] == "number"

    def test_fix_array_schemas_with_anyof(self) -> None:
        """Fixes arrays in anyOf."""
        parameters = {
            "anyOf": [
                {"type": "array"},
                {"type": "string"},
            ]
        }

        fixed = ToolSchemaValidator.fix_array_schemas(parameters)

        assert fixed["anyOf"][0]["items"] == {"type": "string"}

    def test_fix_array_schemas_oneof_allof(self) -> None:
        """Fixes arrays in oneOf and allOf."""
        parameters = {
            "oneOf": [{"type": "array"}],
            "allOf": [{"type": "object", "properties": {"arr": {"type": "array"}}}],
        }

        fixed = ToolSchemaValidator.fix_array_schemas(parameters)

        assert fixed["oneOf"][0]["items"] == {"type": "string"}
        assert fixed["allOf"][0]["properties"]["arr"]["items"] == {"type": "string"}


class TestFixOpenaiCompatibility:
    """Tests for fix_openai_compatibility method."""

    def test_fix_removes_unsupported(self) -> None:
        """Removes unsupported function properties."""
        tool = {
            "type": "function",
            "function": {
                "name": "tool",
                "description": "Test",
                "title": "Remove me",
                "examples": ["example"],
                "deprecated": True,
                "version": "1.0",
                "tags": ["tag1"],
                "summary": "Summary",
                "parameters": {"type": "object"},
            },
        }

        fixed = ToolSchemaValidator.fix_openai_compatibility(tool)

        function = fixed["function"]
        assert "title" not in function
        assert "examples" not in function
        assert "deprecated" not in function
        assert "version" not in function
        assert "tags" not in function
        assert "summary" not in function
        assert "name" in function
        assert "description" in function

    def test_fix_preserves_valid_props(self) -> None:
        """Preserves valid properties."""
        tool = {
            "type": "function",
            "function": {
                "name": "tool",
                "description": "Test",
                "parameters": {
                    "type": "object",
                    "properties": {"arg1": {"type": "string"}},
                },
            },
        }

        fixed = ToolSchemaValidator.fix_openai_compatibility(tool)

        assert fixed["function"]["name"] == "tool"
        assert fixed["function"]["description"] == "Test"
        assert "arg1" in fixed["function"]["parameters"]["properties"]

    def test_fix_also_fixes_arrays(self) -> None:
        """Also fixes array schemas."""
        tool = {
            "type": "function",
            "function": {
                "name": "tool",
                "description": "Test",
                "parameters": {
                    "type": "object",
                    "properties": {"arr": {"type": "array"}},
                },
            },
        }

        fixed = ToolSchemaValidator.fix_openai_compatibility(tool)

        assert "items" in fixed["function"]["parameters"]["properties"]["arr"]

    def test_fix_removes_param_level_props(self) -> None:
        """Removes unsupported parameter properties."""
        tool = {
            "type": "function",
            "function": {
                "name": "tool",
                "description": "Test",
                "parameters": {
                    "type": "object",
                    "title": "Remove me",
                    "examples": ["example"],
                    "deprecated": True,
                    "properties": {},
                },
            },
        }

        fixed = ToolSchemaValidator.fix_openai_compatibility(tool)

        params = fixed["function"]["parameters"]
        assert "title" not in params
        assert "examples" not in params
        assert "deprecated" not in params


class TestValidateAndFixTool:
    """Tests for validate_and_fix_tool method."""

    def test_validate_and_fix_openai_success(self) -> None:
        """Fixes and validates successfully."""
        tool = {
            "type": "function",
            "function": {
                "name": "tool",
                "description": "Test",
                "title": "Remove me",
                "parameters": {"type": "object"},
            },
        }

        is_valid, fixed_tool, error = ToolSchemaValidator.validate_and_fix_tool(
            tool, "openai"
        )

        assert is_valid is True
        assert error is None
        assert "title" not in fixed_tool["function"]

    def test_validate_and_fix_openai_failure(self) -> None:
        """Reports unfixable tools."""
        tool = {
            "type": "function",
            "function": {
                "name": "invalid@name",
                "description": "Test",
            },
        }

        is_valid, fixed_tool, error = ToolSchemaValidator.validate_and_fix_tool(
            tool, "openai"
        )

        assert is_valid is False
        assert error is not None
        assert "invalid characters" in error

    def test_validate_and_fix_non_openai(self) -> None:
        """Non-OpenAI providers pass through."""
        tool = {"name": "any_tool"}

        is_valid, fixed_tool, error = ToolSchemaValidator.validate_and_fix_tool(
            tool, "anthropic"
        )

        assert is_valid is True
        assert error is None
        assert fixed_tool == tool

    def test_validate_and_fix_exception_handling(self) -> None:
        """Handles exceptions gracefully."""
        tool = None  # type: ignore

        is_valid, fixed_tool, error = ToolSchemaValidator.validate_and_fix_tool(
            tool, "openai"  # type: ignore
        )

        assert is_valid is False
        assert error is not None
        assert "Error during fix/validation" in error
