"""Renderer for timeline diagrams.

Renders a vertical timeline with sections and events connected by
a central vertical line.
"""
from __future__ import annotations

from ..model.timeline import Timeline
from .canvas import Canvas
from .charset import ASCII, UNICODE, CharSet


def render_timeline(
    diagram: Timeline,
    *,
    use_ascii: bool = False,
) -> Canvas:
    """Render a Timeline model to a Canvas."""
    cs = ASCII if use_ascii else UNICODE

    if not diagram.sections:
        return Canvas(1, 1)

    # Build lines of output
    lines: list[str] = []

    # Title
    if diagram.title:
        lines.append(diagram.title)
        lines.append("")

    v = "|" if use_ascii else "│"
    h = "-" if use_ascii else "─"
    bullet = "o" if use_ascii else "●"
    section_marker = "=" if use_ascii else "═"

    for si, section in enumerate(diagram.sections):
        # Section header
        if section.title:
            header = f" {section_marker}{section_marker} {section.title} {section_marker}{section_marker}"
            lines.append(header)
            lines.append(f" {v}")

        for ei, event in enumerate(section.events):
            # Event node
            is_last_event = ei == len(section.events) - 1
            is_last_section = si == len(diagram.sections) - 1

            lines.append(f" {bullet}{h}{h} {event.title}")

            # Details indented under the event
            for detail in event.details:
                lines.append(f" {v}   {detail}")

            # Continuation line
            if not (is_last_event and is_last_section):
                lines.append(f" {v}")

    # Write to canvas
    width = max((len(line) for line in lines), default=1) + 1
    height = len(lines)
    canvas = Canvas(width, height)
    for r, line in enumerate(lines):
        canvas.put_text(r, 0, line, style="node")

    return canvas
