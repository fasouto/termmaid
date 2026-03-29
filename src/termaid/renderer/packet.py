"""Renderer for packet diagrams.

Renders network packet field layouts as a grid of bit-aligned boxes,
with bit numbers at field boundaries. Fields wrap to new rows every
row_bits (default 32) bits.
"""
from __future__ import annotations

from ..model.packet import Packet
from ..utils import display_width
from .canvas import Canvas


_BITS_PER_COL = 2  # character columns per bit


def render_packet(
    diagram: Packet,
    *,
    use_ascii: bool = False,
) -> Canvas:
    """Render a Packet model to a Canvas."""
    if not diagram.fields:
        return Canvas(1, 1)

    row_bits = diagram.row_bits
    cols_per_row = row_bits * _BITS_PER_COL

    hz = "-" if use_ascii else "─"
    vt = "|" if use_ascii else "│"
    tl = "+" if use_ascii else "┌"
    tr = "+" if use_ascii else "┐"
    bl = "+" if use_ascii else "└"
    br = "+" if use_ascii else "┘"
    tj = "+" if use_ascii else "┬"
    bj = "+" if use_ascii else "┴"
    lj = "+" if use_ascii else "├"
    rj = "+" if use_ascii else "┤"
    cross = "+" if use_ascii else "┼"

    margin = 1

    # Group fields into rows
    rows: list[list[tuple[int, int, str]]] = []
    for field in diagram.fields:
        bit = field.start
        remaining_label = field.label
        while bit <= field.end:
            row_idx = bit // row_bits
            col_in_row = bit % row_bits
            bits_in_this_row = min(field.end - bit + 1, row_bits - col_in_row)
            col_start = col_in_row
            col_end = col_in_row + bits_in_this_row - 1

            while len(rows) <= row_idx:
                rows.append([])

            rows[row_idx].append((col_start, col_end, remaining_label))
            remaining_label = ""
            bit += bits_in_this_row

    # Each row: 3 lines (bit numbers, top border, content)
    # Last row gets an extra bottom border
    total_h = len(rows) * 3 + 1  # +1 for final bottom border
    total_w = margin + cols_per_row + 1

    canvas = Canvas(total_w + 4, total_h + 1)

    for ri, row_fields in enumerate(rows):
        y_nums = ri * 3
        y_border = ri * 3 + 1
        y_content = ri * 3 + 2
        row_start_bit = ri * row_bits

        # Bit numbers at field boundaries
        for cs, ce, _ in row_fields:
            # Start bit
            bit_num = row_start_bit + cs
            label = str(bit_num)
            x = margin + cs * _BITS_PER_COL
            canvas.put_text(y_nums, x, label, style="edge_label")

        # End bit of last field (right-aligned)
        if row_fields:
            last_ce = row_fields[-1][1]
            bit_num = row_start_bit + last_ce
            label = str(bit_num)
            x = margin + (last_ce + 1) * _BITS_PER_COL - display_width(label)
            canvas.put_text(y_nums, max(0, x), label, style="edge_label")

        # Top border
        for c in range(cols_per_row):
            canvas.put(y_border, margin + c, hz, merge=False, style="node")
        # Right edge
        is_first = ri == 0
        canvas.put(y_border, margin + cols_per_row, tr if is_first else rj, merge=False, style="node")

        # Field separators on border
        for fi, (cs, ce, _) in enumerate(row_fields):
            x = margin + cs * _BITS_PER_COL
            if cs == 0:
                canvas.put(y_border, x, tl if is_first else lj, merge=False, style="node")
            else:
                canvas.put(y_border, x, tj if is_first else cross, merge=False, style="node")

        # Content row
        canvas.put(y_content, margin, vt, merge=False, style="node")
        canvas.put(y_content, margin + cols_per_row, vt, merge=False, style="node")

        for cs, ce, label in row_fields:
            x_start = margin + cs * _BITS_PER_COL
            x_end = margin + (ce + 1) * _BITS_PER_COL
            field_w = x_end - x_start

            # Field separator
            if cs > 0:
                canvas.put(y_content, x_start, vt, merge=False, style="node")

            # Center label
            if label:
                avail = field_w - 2
                disp_label = label
                if display_width(disp_label) > avail:
                    disp_label = label[:max(1, avail - 1)] + "."
                lx = x_start + 1 + (avail - display_width(disp_label)) // 2
                canvas.put_text(y_content, lx, disp_label, style="label")

    # Bottom border
    y_bottom = len(rows) * 3
    for c in range(cols_per_row):
        canvas.put(y_bottom, margin + c, hz, merge=False, style="node")
    canvas.put(y_bottom, margin, bl, merge=False, style="node")
    canvas.put(y_bottom, margin + cols_per_row, br, merge=False, style="node")

    # Bottom border field separators
    if rows:
        for cs, ce, _ in rows[-1]:
            if cs > 0:
                x = margin + cs * _BITS_PER_COL
                canvas.put(y_bottom, x, bj, merge=False, style="node")

    return canvas
