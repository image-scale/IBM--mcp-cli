"""Tests for display formatters."""

from __future__ import annotations

from mcpcli.display.formatters import (
    format_args_preview,
    format_reasoning_preview,
    format_content_preview,
)


class TestFormatArgsPreview:
    """Tests for format_args_preview function."""

    def test_empty_arguments(self) -> None:
        """Empty dict returns empty string."""
        result = format_args_preview({})
        assert result == ""

    def test_single_string_argument(self) -> None:
        """Single string argument formatted correctly."""
        result = format_args_preview({"name": "test"})
        assert result == "name=test"

    def test_multiple_arguments_within_limit(self) -> None:
        """Multiple arguments shown with commas."""
        result = format_args_preview({"host": "localhost", "port": "8080"})
        assert "host=localhost" in result
        assert "port=8080" in result

    def test_more_than_max_args(self) -> None:
        """Shows first N args with +N more indicator."""
        args = {"a": "1", "b": "2", "c": "3", "d": "4"}
        result = format_args_preview(args, max_args=2)

        assert "a=1" in result
        assert "b=2" in result
        assert "+2 more" in result
        assert "c=3" not in result

    def test_long_string_value_truncated(self) -> None:
        """Long string values are truncated."""
        long_str = "x" * 100
        result = format_args_preview({"data": long_str}, max_len=40)

        assert "data=" in result
        assert "..." in result
        assert len(result) < 100

    def test_dict_value(self) -> None:
        """Dict values formatted as JSON."""
        result = format_args_preview({"config": {"key": "value"}})
        assert "config=" in result
        assert "key" in result
        assert "value" in result

    def test_list_value(self) -> None:
        """List values formatted as JSON."""
        result = format_args_preview({"items": [1, 2, 3]})
        assert "items=" in result
        assert "1" in result
        assert "2" in result
        assert "3" in result

    def test_large_dict_value_truncated(self) -> None:
        """Large dict values are truncated."""
        large_dict = {f"key_{i}": f"value_{i}" for i in range(20)}
        result = format_args_preview({"data": large_dict}, max_len=40)

        assert "data=" in result
        assert "..." in result

    def test_large_list_value_truncated(self) -> None:
        """Large list values are truncated."""
        large_list = list(range(50))
        result = format_args_preview({"numbers": large_list}, max_len=40)

        assert "numbers=" in result
        assert "..." in result

    def test_integer_value(self) -> None:
        """Integer values formatted correctly."""
        result = format_args_preview({"count": 42})
        assert "count=42" in result

    def test_boolean_value(self) -> None:
        """Boolean values formatted correctly."""
        result = format_args_preview({"enabled": True})
        assert "enabled=True" in result

    def test_none_value(self) -> None:
        """None values formatted correctly."""
        result = format_args_preview({"optional": None})
        assert "optional=None" in result

    def test_custom_max_args(self) -> None:
        """Custom max_args respected."""
        args = {"a": "1", "b": "2", "c": "3"}
        result = format_args_preview(args, max_args=3)

        assert "a=1" in result
        assert "b=2" in result
        assert "c=3" in result
        assert "more" not in result

    def test_custom_max_len(self) -> None:
        """Custom max_len respected."""
        result = format_args_preview({"data": "x" * 100}, max_len=10)

        assert "..." in result
        assert len(result) < 50


class TestFormatReasoningPreview:
    """Tests for format_reasoning_preview function."""

    def test_empty_reasoning(self) -> None:
        """Empty string returns empty string."""
        result = format_reasoning_preview("")
        assert result == ""

    def test_short_reasoning(self) -> None:
        """Short reasoning returned as-is."""
        short = "This is short"
        result = format_reasoning_preview(short)
        assert result == short

    def test_long_reasoning_from_end(self) -> None:
        """Long reasoning shows last N chars by default."""
        long_text = "The quick brown fox jumps over the lazy dog. This is the end part."
        result = format_reasoning_preview(long_text, max_len=30, from_end=True)

        assert result.startswith("...")
        assert "end part" in result
        assert "quick" not in result

    def test_long_reasoning_from_start(self) -> None:
        """Long reasoning can show first N chars."""
        long_text = "This is the start. More text here. And even more at the end."
        result = format_reasoning_preview(long_text, max_len=30, from_end=False)

        assert result.endswith("...")
        assert "start" in result
        assert "end" not in result

    def test_word_boundary_from_end(self) -> None:
        """Tries to break at word boundary from end."""
        text = "word1 word2 word3 word4 word5 word6"
        result = format_reasoning_preview(text, max_len=20, from_end=True)

        assert "..." in result
        words_in_result = result.replace("...", "").strip().split()
        assert all(word in text for word in words_in_result)

    def test_word_boundary_from_start(self) -> None:
        """Tries to break at word boundary from start."""
        text = "word1 word2 word3 word4 word5 word6"
        result = format_reasoning_preview(text, max_len=20, from_end=False)

        assert "..." in result
        words_in_result = result.replace("...", "").strip().split()
        assert all(word in text for word in words_in_result)

    def test_no_spaces_from_end(self) -> None:
        """Handles text with no spaces from end."""
        text = "x" * 100
        result = format_reasoning_preview(text, max_len=30, from_end=True)

        assert result.startswith("...")
        assert len(result) <= 35

    def test_no_spaces_from_start(self) -> None:
        """Handles text with no spaces from start."""
        text = "x" * 100
        result = format_reasoning_preview(text, max_len=30, from_end=False)

        assert result.endswith("...")
        assert len(result) <= 35

    def test_exact_length(self) -> None:
        """Text exactly at max_len returned as-is."""
        text = "x" * 50
        result = format_reasoning_preview(text, max_len=50)

        assert result == text

    def test_custom_max_len(self) -> None:
        """Custom max_len respected."""
        text = "x" * 100
        result = format_reasoning_preview(text, max_len=10)

        assert "..." in result
        assert len(result) <= 15


class TestFormatContentPreview:
    """Tests for format_content_preview function."""

    def test_empty_content(self) -> None:
        """Empty string returns empty string."""
        result = format_content_preview("")
        assert result == ""

    def test_short_content(self) -> None:
        """Short content returned as-is."""
        short = "Short text"
        result = format_content_preview(short)
        assert result == short

    def test_long_content(self) -> None:
        """Long content truncated with ellipsis."""
        long_text = "x" * 200
        result = format_content_preview(long_text, max_len=100)

        assert result.endswith("...")
        assert len(result) <= 110

    def test_word_boundary_breaking(self) -> None:
        """Breaks at word boundaries when possible."""
        text = "The quick brown fox jumps over the lazy dog. More text here."
        result = format_content_preview(text, max_len=30)

        assert result.endswith("...")
        words = result.replace("...", "").strip().split()
        assert all(word in text for word in words)

    def test_word_boundary_too_early(self) -> None:
        """Word boundary only used if reasonably far."""
        text = "a " + "x" * 200
        result = format_content_preview(text, max_len=100)

        assert len(result) > 50

    def test_no_spaces(self) -> None:
        """Content with no spaces truncated correctly."""
        text = "x" * 200
        result = format_content_preview(text, max_len=100)

        assert result.endswith("...")
        assert len(result) <= 105

    def test_exact_length(self) -> None:
        """Content exactly at max_len returned as-is."""
        text = "x" * 100
        result = format_content_preview(text, max_len=100)

        assert result == text

    def test_custom_max_len(self) -> None:
        """Custom max_len respected."""
        text = "x" * 200
        result = format_content_preview(text, max_len=50)

        assert result.endswith("...")
        assert len(result) <= 55

    def test_multiline_content(self) -> None:
        """Multiline content handled correctly."""
        text = "Line 1\nLine 2\nLine 3\n" + "More text " * 20
        result = format_content_preview(text, max_len=50)

        assert result.endswith("...")
        assert len(result) <= 55
