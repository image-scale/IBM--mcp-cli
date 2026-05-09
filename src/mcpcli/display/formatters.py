"""Preview formatters for display components.

Provides formatting utilities for creating inline previews of tool arguments,
reasoning content, and other display elements.
"""

from __future__ import annotations

import json
from typing import Any


def format_args_preview(
    arguments: dict[str, Any],
    max_args: int = 4,
    max_len: int = 60,
) -> str:
    """Format tool arguments for inline preview.

    Shows first N arguments, truncated to reasonable length.

    Args:
        arguments: Tool arguments dictionary.
        max_args: Maximum number of arguments to show.
        max_len: Maximum length for each argument value.

    Returns:
        Formatted preview string like "key1=val1, key2=val2 +N more".
    """
    if not arguments:
        return ""

    preview_items: list[str] = []
    for key, value in list(arguments.items())[:max_args]:
        if isinstance(value, str):
            val_str = value[:max_len] + "..." if len(value) > max_len else value
        elif isinstance(value, (dict, list)):
            json_str = json.dumps(value)
            val_str = json_str[:max_len] + "..." if len(json_str) > max_len else json_str
        else:
            val_str = str(value)[:max_len]

        preview_items.append(f"{key}={val_str}")

    result = ", ".join(preview_items)

    if len(arguments) > max_args:
        result += f" +{len(arguments) - max_args} more"

    return result


def format_reasoning_preview(
    reasoning: str,
    max_len: int = 50,
    from_end: bool = True,
) -> str:
    """Format reasoning content for inline preview.

    Shows a clean excerpt of the reasoning with proper word boundaries.
    By default shows last N chars (most recent thinking).

    Args:
        reasoning: Full reasoning content.
        max_len: Maximum length to show.
        from_end: Whether to show from end (recent) or beginning.

    Returns:
        Formatted preview string with ellipsis and clean word boundaries.
    """
    if not reasoning:
        return ""

    cleaned = " ".join(reasoning.split())

    if len(cleaned) <= max_len:
        return cleaned

    if from_end:
        preview = cleaned[-(max_len):]

        first_space = preview.find(" ")
        if 0 < first_space < len(preview) // 2:
            preview = preview[first_space + 1:]

        return f"...{preview}"
    else:
        preview = cleaned[:max_len]

        last_space = preview.rfind(" ")
        if last_space > max_len // 2:
            preview = preview[:last_space]

        return f"{preview}..."


def format_content_preview(
    content: str,
    max_len: int = 100,
) -> str:
    """Format content for inline preview.

    Truncates content to max_len, trying to break at word boundaries.

    Args:
        content: Full content to preview.
        max_len: Maximum length to show.

    Returns:
        Formatted preview string with ellipsis if truncated.
    """
    if not content:
        return ""

    if len(content) <= max_len:
        return content

    preview = content[:max_len]
    space_idx = preview.rfind(" ")
    if space_idx > max_len // 2:
        preview = preview[:space_idx]

    return f"{preview}..."


__all__ = [
    "format_args_preview",
    "format_reasoning_preview",
    "format_content_preview",
]
