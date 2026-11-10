# SPDX-License-Identifier: Apache-2.0

"""Shared constants and tiny helpers for TUI output."""

from rich.text import Text


def status_icon(success: bool) -> Text:
    """Return a colored ✓ or ✗."""
    if success:
        return Text("✓", style="green")
    return Text("✗", style="red")
