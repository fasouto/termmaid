"""Plain text output adapter."""
from __future__ import annotations

from ..graph.model import Graph
from ..renderer.draw import render_graph


def render_text(
    graph: Graph,
    use_ascii: bool = False,
    padding_x: int = 4,
    padding_y: int = 2,
    rounded_edges: bool = True,
) -> str:
    """Render a graph to plain text."""
    return render_graph(graph, use_ascii=use_ascii, padding_x=padding_x, padding_y=padding_y, rounded_edges=rounded_edges)
