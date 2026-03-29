"""Parser for Mermaid architecture diagrams.

Converts architecture-beta syntax into a Graph model so it can
be rendered using the existing flowchart renderer.

Syntax:
    architecture-beta
        group api(cloud)[API]
        service db(database)[Database] in api
        service server(server)[Server] in api
        db:R --> L:server
"""
from __future__ import annotations

import re

from ..graph.model import Direction, Edge, Graph, Node, Subgraph
from ..graph.shapes import NodeShape


# Map architecture icons to node shapes.
# Use simple rectangles for all - the emoji icon already indicates the type.
_ICON_SHAPES = {
    "cloud": NodeShape.RECTANGLE,
    "database": NodeShape.RECTANGLE,
    "disk": NodeShape.RECTANGLE,
    "server": NodeShape.RECTANGLE,
    "internet": NodeShape.RECTANGLE,
}

# Icon prefixes for labels
_ICON_PREFIX = {
    "cloud": "☁ ",
    "database": "🗄 ",
    "disk": "💾 ",
    "server": "🖥 ",
    "internet": "🌐 ",
}


def parse_architecture(text: str) -> Graph:
    """Parse an architecture-beta diagram into a Graph model."""
    lines = text.strip().splitlines()
    graph = Graph(direction=Direction.LR)

    if not lines:
        return graph

    groups: dict[str, Subgraph] = {}
    services: dict[str, str] = {}  # id -> parent group id

    for line in lines[1:]:  # skip "architecture-beta" header
        comment_idx = line.find("%%")
        if comment_idx >= 0:
            line = line[:comment_idx]

        stripped = line.strip()
        if not stripped:
            continue

        # Group: group id(icon)[label] [in parent]
        m = re.match(r'^group\s+(\w+)(?:\((\w+)\))?\[([^\]]*)\](?:\s+in\s+(\w+))?', stripped)
        if m:
            gid = m.group(1)
            icon = m.group(2) or ""
            label = m.group(3)
            parent_id = m.group(4)

            sg = Subgraph(id=gid, label=label)
            if parent_id and parent_id in groups:
                groups[parent_id].children.append(sg)
                sg.parent = groups[parent_id]
            else:
                graph.subgraphs.append(sg)
            groups[gid] = sg
            continue

        # Service: service id(icon)[label] [in group]
        m = re.match(r'^service\s+(\w+)(?:\((\w+)\))?\[([^\]]*)\](?:\s+in\s+(\w+))?', stripped)
        if m:
            sid = m.group(1)
            icon = m.group(2) or ""
            label = m.group(3)
            parent_id = m.group(4)

            # Add icon prefix to label
            prefix = _ICON_PREFIX.get(icon, "")
            shape = _ICON_SHAPES.get(icon, NodeShape.RECTANGLE)

            node = Node(id=sid, label=prefix + label, shape=shape)
            graph.add_node(node)

            if parent_id and parent_id in groups:
                groups[parent_id].node_ids.append(sid)
                services[sid] = parent_id
            continue

        # Junction: junction id [in group]
        m = re.match(r'^junction\s+(\w+)(?:\s+in\s+(\w+))?', stripped)
        if m:
            jid = m.group(1)
            parent_id = m.group(2)

            node = Node(id=jid, label="", shape=NodeShape.DIAMOND)
            graph.add_node(node)

            if parent_id and parent_id in groups:
                groups[parent_id].node_ids.append(jid)
            continue

        # Edge: id{group}?:DIR arrow--arrow DIR:id{group}?
        # Simplified: look for --> or -- patterns
        m = re.match(
            r'^(\w+)(?:\{(\w+)\})?:([LRTB])\s+'
            r'(<?)--(-?)(>?)\s+'
            r'([LRTB]):(\w+)(?:\{(\w+)\})?',
            stripped,
        )
        if m:
            src = m.group(1)
            # src_group = m.group(2)
            # src_dir = m.group(3)
            has_arrow_start = m.group(4) == "<"
            has_arrow_end = m.group(6) == ">"
            tgt = m.group(8)
            # tgt_group = m.group(9)

            edge = Edge(
                source=src,
                target=tgt,
                has_arrow_start=has_arrow_start,
                has_arrow_end=has_arrow_end,
            )
            graph.add_edge(edge)
            continue

        # Simpler edge format: id --> id or id -- id
        m = re.match(r'^(\w+)\s*(<?)--(-?)(>?)\s*(\w+)', stripped)
        if m:
            src = m.group(1)
            has_arrow_start = m.group(2) == "<"
            has_arrow_end = m.group(4) == ">"
            tgt = m.group(5)

            edge = Edge(
                source=src,
                target=tgt,
                has_arrow_start=has_arrow_start,
                has_arrow_end=has_arrow_end,
            )
            graph.add_edge(edge)

    return graph
