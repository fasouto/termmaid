"""2D character canvas for rendering diagrams.

Row-major indexing: canvas[row][col] holds a single character.
Supports junction merging when box-drawing characters overlap.
"""
from __future__ import annotations

from .charset import CharSet, UNICODE


# Junction merging lookup table
# Maps (existing_char, new_char) -> merged_char for Unicode box-drawing
_JUNCTION_TABLE: dict[tuple[str, str], str] = {}


def _build_junction_table() -> None:
    """Build the junction merge lookup table."""
    # Horizontal + Vertical = Cross
    pairs = [
        ("─", "│", "┼"),
        ("│", "─", "┼"),
        # Horizontal + corners = T-junctions
        ("─", "┌", "┬"), ("─", "┐", "┬"),
        ("─", "└", "┴"), ("─", "┘", "┴"),
        ("┌", "─", "┬"), ("┐", "─", "┬"),
        ("└", "─", "┴"), ("┘", "─", "┴"),
        # Vertical + corners = T-junctions
        ("│", "┌", "├"), ("│", "└", "├"),
        ("│", "┐", "┤"), ("│", "┘", "┤"),
        ("┌", "│", "├"), ("└", "│", "├"),
        ("┐", "│", "┤"), ("┘", "│", "┤"),
        # T-junctions + lines = cross
        ("├", "─", "┼"), ("┤", "─", "┼"),
        ("┬", "│", "┼"), ("┴", "│", "┼"),
        ("─", "├", "┼"), ("─", "┤", "┼"),
        ("│", "┬", "┼"), ("│", "┴", "┼"),
        # T-junction + corner
        ("├", "┐", "┼"), ("├", "┘", "┼"),
        ("┤", "┌", "┼"), ("┤", "└", "┼"),
        ("┬", "└", "┼"), ("┬", "┘", "┼"),
        ("┴", "┌", "┼"), ("┴", "┐", "┼"),
        # T-junctions combining
        ("├", "┤", "┼"), ("┤", "├", "┼"),
        ("┬", "┴", "┼"), ("┴", "┬", "┼"),
        # Corners combining
        ("┌", "┘", "┼"), ("┘", "┌", "┼"),
        ("┐", "└", "┼"), ("└", "┐", "┼"),
        ("┌", "┐", "┬"), ("┐", "┌", "┬"),
        ("└", "┘", "┴"), ("┘", "└", "┴"),
        ("┌", "└", "├"), ("└", "┌", "├"),
        ("┐", "┘", "┤"), ("┘", "┐", "┤"),
        # Thick lines
        ("━", "┃", "╋"),
        ("┃", "━", "╋"),
        # Dotted lines
        ("┄", "┆", "┼"),
        ("┆", "┄", "┼"),
        # Mixed line styles with junctions
        ("─", "┃", "┼"), ("┃", "─", "┼"),
        ("━", "│", "┼"), ("│", "━", "┼"),
        # Rounded corners with lines = T-junctions
        ("─", "╭", "┬"), ("─", "╮", "┬"),
        ("─", "╰", "┴"), ("─", "╯", "┴"),
        ("╭", "─", "┬"), ("╮", "─", "┬"),
        ("╰", "─", "┴"), ("╯", "─", "┴"),
        ("│", "╭", "├"), ("│", "╰", "├"),
        ("│", "╮", "┤"), ("│", "╯", "┤"),
        ("╭", "│", "├"), ("╰", "│", "├"),
        ("╮", "│", "┤"), ("╯", "│", "┤"),
        # Rounded corners combining
        ("╭", "╯", "┼"), ("╯", "╭", "┼"),
        ("╮", "╰", "┼"), ("╰", "╮", "┼"),
        ("╭", "╮", "┬"), ("╮", "╭", "┬"),
        ("╰", "╯", "┴"), ("╯", "╰", "┴"),
        ("╭", "╰", "├"), ("╰", "╭", "├"),
        ("╮", "╯", "┤"), ("╯", "╮", "┤"),
        # Rounded + T-junctions = cross
        ("├", "╮", "┼"), ("├", "╯", "┼"),
        ("┤", "╭", "┼"), ("┤", "╰", "┼"),
        ("┬", "╰", "┼"), ("┬", "╯", "┼"),
        ("┴", "╭", "┼"), ("┴", "╮", "┼"),
        # Double-line borders merging with single-line edges
        ("═", "│", "┼"), ("│", "═", "┼"),
        ("║", "─", "┼"), ("─", "║", "┼"),
        ("╔", "─", "┬"), ("╗", "─", "┬"),
        ("╚", "─", "┴"), ("╝", "─", "┴"),
        ("╔", "│", "├"), ("╚", "│", "├"),
        ("╗", "│", "┤"), ("╝", "│", "┤"),
        ("║", "┌", "├"), ("║", "└", "├"),
        ("║", "┐", "┤"), ("║", "┘", "┤"),
        ("═", "┌", "┬"), ("═", "┐", "┬"),
        ("═", "└", "┴"), ("═", "┘", "┴"),
    ]
    # Shape markers (◆ for diamond, ◯ for circle) are immovable:
    # any box-drawing char merging with them keeps the marker.
    _all_box = set("─│┌┐└┘├┤┬┴┼━┃╋┄┆╭╮╰╯═║╔╗╚╝")
    for marker in ("◆", "◇", "◯"):
        for bc in _all_box:
            pairs.append((marker, bc, marker))
            pairs.append((bc, marker, marker))
    for existing, new, merged in pairs:
        _JUNCTION_TABLE[(existing, new)] = merged


_build_junction_table()

# Set of all box-drawing characters that participate in junction merging
_BOX_CHARS = set("─│┌┐└┘├┤┬┴┼━┃╋┄┆╭╮╰╯═║╔╗╚╝◆◇◯")


class Canvas:
    """2D character canvas with row-major indexing."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self._grid: list[list[str]] = [
            [" " for _ in range(width)] for _ in range(height)
        ]
        self._style_grid: list[list[str]] = [
            ["default" for _ in range(width)] for _ in range(height)
        ]

    def resize(self, new_width: int, new_height: int) -> None:
        """Expand the canvas to at least the given dimensions."""
        if new_width <= self.width and new_height <= self.height:
            return
        new_w = max(self.width, new_width)
        new_h = max(self.height, new_height)
        for r in range(self.height):
            self._grid[r].extend(" " for _ in range(new_w - self.width))
            self._style_grid[r].extend("default" for _ in range(new_w - self.width))
        for _ in range(new_h - self.height):
            self._grid.append([" " for _ in range(new_w)])
            self._style_grid.append(["default" for _ in range(new_w)])
        self.width = new_w
        self.height = new_h

    def get(self, row: int, col: int) -> str:
        if 0 <= row < self.height and 0 <= col < self.width:
            return self._grid[row][col]
        return " "

    def put(self, row: int, col: int, ch: str, merge: bool = True, style: str = "") -> None:
        """Place a character on the canvas, optionally merging junctions."""
        if not (0 <= row < self.height and 0 <= col < self.width):
            return
        if ch == " ":
            return

        existing = self._grid[row][col]
        if existing == " ":
            self._grid[row][col] = ch
        elif merge and existing in _BOX_CHARS and ch in _BOX_CHARS:
            merged = _JUNCTION_TABLE.get((existing, ch))
            if merged:
                self._grid[row][col] = merged
            else:
                self._grid[row][col] = ch
        else:
            self._grid[row][col] = ch

        if style:
            self._style_grid[row][col] = style

    def put_text(self, row: int, col: int, text: str, style: str = "") -> None:
        """Place a string of characters starting at (row, col)."""
        for i, ch in enumerate(text):
            self.put(row, col + i, ch, merge=False, style=style)

    def put_styled_text(self, row: int, col: int, segments: list[tuple[str, str]]) -> None:
        """Place text with per-segment style keys. Each segment is (text, style_key)."""
        offset = 0
        for text, style in segments:
            for ch in text:
                self.put(row, col + offset, ch, merge=False, style=style)
                offset += 1

    def get_style(self, row: int, col: int) -> str:
        """Get the style key at a position."""
        if 0 <= row < self.height and 0 <= col < self.width:
            return self._style_grid[row][col]
        return "default"

    def to_styled_pairs(self) -> list[list[tuple[str, str]]]:
        """Return (char, style_key) pairs for each cell."""
        result: list[list[tuple[str, str]]] = []
        for r in range(self.height):
            row_pairs: list[tuple[str, str]] = []
            for c in range(self.width):
                row_pairs.append((self._grid[r][c], self._style_grid[r][c]))
            result.append(row_pairs)
        return result

    def draw_horizontal(self, row: int, col_start: int, col_end: int, ch: str, style: str = "") -> None:
        """Draw a horizontal line."""
        c_min, c_max = min(col_start, col_end), max(col_start, col_end)
        for c in range(c_min, c_max + 1):
            self.put(row, c, ch, style=style)

    def draw_vertical(self, col: int, row_start: int, row_end: int, ch: str, style: str = "") -> None:
        """Draw a vertical line."""
        r_min, r_max = min(row_start, row_end), max(row_start, row_end)
        for r in range(r_min, r_max + 1):
            self.put(r, col, ch, style=style)

    def to_string(self) -> str:
        """Convert canvas to a string, trimming trailing whitespace per line."""
        lines: list[str] = []
        for row in self._grid:
            line = "".join(row).rstrip()
            lines.append(line)
        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines)

    def flip_vertical(self) -> None:
        """Flip the canvas vertically (for BT direction)."""
        self._grid.reverse()
        self._style_grid.reverse()
        # Remap characters
        _flip_map = {
            "┌": "└", "┐": "┘", "└": "┌", "┘": "┐",
            "├": "├", "┤": "┤", "┬": "┴", "┴": "┬",
            "▼": "▲", "▲": "▼",
            "╭": "╰", "╮": "╯", "╰": "╭", "╯": "╮",
            "v": "^", "^": "v",
            "╔": "╚", "╗": "╝", "╚": "╔", "╝": "╗",
        }
        for r in range(self.height):
            for c in range(self.width):
                ch = self._grid[r][c]
                if ch in _flip_map:
                    self._grid[r][c] = _flip_map[ch]

    def flip_horizontal(self) -> None:
        """Flip the canvas horizontally (for RL direction)."""
        for r in range(self.height):
            self._grid[r].reverse()
            self._style_grid[r].reverse()
        _flip_map = {
            "┌": "┐", "┐": "┌", "└": "┘", "┘": "└",
            "├": "┤", "┤": "├", "┬": "┬", "┴": "┴",
            "►": "◄", "◄": "►",
            "╭": "╮", "╮": "╭", "╰": "╯", "╯": "╰",
            ">": "<", "<": ">",
            "╔": "╗", "╗": "╔", "╚": "╝", "╝": "╚",
        }
        for r in range(self.height):
            for c in range(self.width):
                ch = self._grid[r][c]
                if ch in _flip_map:
                    self._grid[r][c] = _flip_map[ch]
