"""Renderer for treemap diagrams.

Renders a Treemap as nested rectangles on a Canvas using a
squarified layout algorithm for readable proportions.
"""
from __future__ import annotations

from ..model.treemap import Treemap, TreemapNode
from .canvas import Canvas
from .charset import ASCII, UNICODE, CharSet

_MARGIN = 1
_MIN_BOX_W = 4
_MIN_BOX_H = 3
_HEADER_H = 1  # rows reserved for section label inside its border


def render_treemap(
    diagram: Treemap,
    *,
    use_ascii: bool = False,
) -> Canvas:
    """Render a Treemap model to a Canvas."""
    cs = ASCII if use_ascii else UNICODE

    if not diagram.roots:
        return Canvas(1, 1)

    total = diagram.total_value
    if total <= 0:
        return Canvas(1, 1)

    # Size the canvas proportional to total value
    canvas_w = max(60, min(120, int(total ** 0.5) * 4 + 20))
    canvas_h = max(20, min(50, int(total ** 0.5) * 2 + 10))

    canvas = Canvas(canvas_w, canvas_h)

    # Layout the roots into the full canvas area
    _layout_nodes(canvas, cs, diagram.roots, 0, 0, canvas_w, canvas_h, depth=0)

    return canvas


def _layout_nodes(
    canvas: Canvas,
    cs: CharSet,
    nodes: list[TreemapNode],
    x: int, y: int, w: int, h: int,
    depth: int,
) -> None:
    """Recursively lay out nodes into the given rectangle using squarified slicing."""
    if not nodes or w < _MIN_BOX_W or h < _MIN_BOX_H:
        return

    total = sum(n.total_value for n in nodes)
    if total <= 0:
        return

    # Sort by value descending for better squarification
    sorted_nodes = sorted(nodes, key=lambda n: n.total_value, reverse=True)

    # Slice alternating between horizontal and vertical
    horizontal = w >= h

    _slice_layout(canvas, cs, sorted_nodes, x, y, w, h, horizontal, total, depth)


def _slice_layout(
    canvas: Canvas,
    cs: CharSet,
    nodes: list[TreemapNode],
    x: int, y: int, w: int, h: int,
    horizontal: bool,
    total: float,
    depth: int,
) -> None:
    """Lay out nodes by slicing along one axis."""
    remaining = total
    pos = 0  # running position along the slicing axis
    extent = w if horizontal else h

    for i, node in enumerate(nodes):
        frac = node.total_value / remaining if remaining > 0 else 0
        remaining_extent = extent - pos

        if i == len(nodes) - 1:
            # Last node takes whatever is left
            size = remaining_extent
        else:
            size = max(
                _MIN_BOX_W if horizontal else _MIN_BOX_H,
                round(frac * remaining_extent),
            )

        remaining -= node.total_value

        if horizontal:
            bx, by, bw, bh = x + pos, y, size, h
        else:
            bx, by, bw, bh = x, y + pos, w, size

        # Clamp
        bw = max(_MIN_BOX_W, min(bw, w - (bx - x)))
        bh = max(_MIN_BOX_H, min(bh, h - (by - y)))

        _draw_node(canvas, cs, node, bx, by, bw, bh, depth)

        pos += size


def _draw_node(
    canvas: Canvas,
    cs: CharSet,
    node: TreemapNode,
    x: int, y: int, w: int, h: int,
    depth: int,
) -> None:
    """Draw a single node box and recurse into children."""
    if w < _MIN_BOX_W or h < _MIN_BOX_H:
        return

    # Draw box border
    tl = cs.round_top_left if depth == 0 else cs.top_left
    tr = cs.round_top_right if depth == 0 else cs.top_right
    bl = cs.round_bottom_left if depth == 0 else cs.bottom_left
    br = cs.round_bottom_right if depth == 0 else cs.bottom_right
    hz = cs.horizontal
    vt = cs.vertical

    style = "node" if depth == 0 else "subgraph"

    # Top border
    canvas.put(y, x, tl, merge=False, style=style)
    for c in range(x + 1, x + w - 1):
        canvas.put(y, c, hz, merge=False, style=style)
    canvas.put(y, x + w - 1, tr, merge=False, style=style)

    # Bottom border
    canvas.put(y + h - 1, x, bl, merge=False, style=style)
    for c in range(x + 1, x + w - 1):
        canvas.put(y + h - 1, c, hz, merge=False, style=style)
    canvas.put(y + h - 1, x + w - 1, br, merge=False, style=style)

    # Side borders
    for r in range(y + 1, y + h - 1):
        canvas.put(r, x, vt, merge=False, style=style)
        canvas.put(r, x + w - 1, vt, merge=False, style=style)

    # Label
    label = node.label
    inner_w = w - 2
    if len(label) > inner_w:
        label = label[:inner_w - 1] + "…" if inner_w > 1 else label[:inner_w]
    label_col = x + 1 + max(0, (inner_w - len(label)) // 2)
    canvas.put_text(y + 1, label_col, label, style="label")

    # Value (for leaves)
    if not node.children and node.value > 0 and h >= 4:
        val_str = f"{node.value:g}"
        if len(val_str) > inner_w:
            val_str = val_str[:inner_w]
        val_col = x + 1 + max(0, (inner_w - len(val_str)) // 2)
        canvas.put_text(y + 2, val_col, val_str, style="edge_label")

    # Recurse into children
    if node.children:
        # Children go inside the box, below the label
        inner_x = x + 1
        inner_y = y + 2  # skip border + label row
        inner_w = w - 2
        inner_h = h - 3  # border top + label + border bottom

        if inner_w >= _MIN_BOX_W and inner_h >= _MIN_BOX_H:
            _layout_nodes(canvas, cs, node.children, inner_x, inner_y, inner_w, inner_h, depth + 1)
