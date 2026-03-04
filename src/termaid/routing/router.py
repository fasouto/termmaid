"""Edge routing orchestrator.

Determines start/end attachment points on nodes, runs A* pathfinding,
and handles direction selection (preferred vs alternative paths).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from ..graph.model import Direction, Edge, Graph
from ..layout.grid import GridLayout, NodePlacement, SubgraphBounds
from .pathfinder import find_path, simplify_path


class AttachDir(Enum):
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()


@dataclass
class RoutedEdge:
    """An edge with its computed path in grid coordinates."""
    edge: Edge
    # Path as grid coordinates (simplified to corners)
    grid_path: list[tuple[int, int]] = field(default_factory=list)
    # Path as drawing coordinates
    draw_path: list[tuple[int, int]] = field(default_factory=list)
    start_dir: AttachDir = AttachDir.RIGHT
    end_dir: AttachDir = AttachDir.LEFT
    label: str = ""
    index: int = 0
    # Grid cells occupied by this edge's path
    occupied_cells: set[tuple[int, int]] = field(default_factory=set)


def route_edges(graph: Graph, layout: GridLayout) -> list[RoutedEdge]:
    """Route all edges in the graph."""
    direction = graph.direction.normalized()
    routed: list[RoutedEdge] = []
    soft_obstacles: set[tuple[int, int]] = set()

    # Build subgraph bounds lookup
    sg_bounds: dict[str, SubgraphBounds] = {}
    for sb in layout.subgraph_bounds:
        sg_bounds[sb.subgraph.id] = sb

    for i, edge in enumerate(graph.edges):
        src = _resolve_placement(edge.source, edge.source_is_subgraph, layout, sg_bounds)
        tgt = _resolve_placement(edge.target, edge.target_is_subgraph, layout, sg_bounds)

        if src is None or tgt is None:
            continue

        if edge.is_self_reference and not edge.source_is_subgraph:
            re = _route_self_edge(edge, src, layout, direction)
            re.index = i
            routed.append(re)
            continue

        re = _route_edge(edge, src, tgt, layout, direction, soft_obstacles)
        re.index = i
        soft_obstacles.update(re.occupied_cells)
        routed.append(re)

    return routed


def _resolve_placement(
    node_id: str,
    is_subgraph: bool,
    layout: GridLayout,
    sg_bounds: dict[str, SubgraphBounds],
) -> NodePlacement | None:
    """Resolve a node or subgraph ID to a NodePlacement."""
    if not is_subgraph:
        return layout.placements.get(node_id)

    sb = sg_bounds.get(node_id)
    if sb is None:
        return None

    # Synthesize a virtual placement at the subgraph center
    cx = sb.x + sb.width // 2
    cy = sb.y + sb.height // 2
    # Find the closest grid cell to the subgraph center
    best_col = 0
    best_row = 0
    best_dist = float("inf")
    for p in layout.placements.values():
        dx = p.draw_x + p.draw_width // 2 - cx
        dy = p.draw_y + p.draw_height // 2 - cy
        dist = abs(dx) + abs(dy)
        if dist < best_dist:
            best_dist = dist
            best_col = p.grid.col
            best_row = p.grid.row

    from ..layout.grid import GridCoord
    return NodePlacement(
        node_id=node_id,
        grid=GridCoord(col=best_col, row=best_row),
        draw_x=sb.x,
        draw_y=sb.y,
        draw_width=sb.width,
        draw_height=sb.height,
    )


def _get_attach_point(
    placement: NodePlacement,
    attach_dir: AttachDir,
) -> tuple[int, int]:
    """Get the grid coordinate of an attachment point on a node."""
    gc = placement.grid
    if attach_dir == AttachDir.TOP:
        return (gc.col, gc.row - 1)
    elif attach_dir == AttachDir.BOTTOM:
        return (gc.col, gc.row + 1)
    elif attach_dir == AttachDir.LEFT:
        return (gc.col - 1, gc.row)
    else:  # RIGHT
        return (gc.col + 1, gc.row)


def _determine_directions(
    src: NodePlacement,
    tgt: NodePlacement,
    direction: Direction,
) -> tuple[tuple[AttachDir, AttachDir], tuple[AttachDir, AttachDir]]:
    """Determine preferred and alternative start/end attachment directions."""
    sc, sr = src.grid.col, src.grid.row
    tc, tr = tgt.grid.col, tgt.grid.row

    if direction.is_horizontal:
        # Primary flow is left-to-right
        if tc > sc:
            preferred = (AttachDir.RIGHT, AttachDir.LEFT)
        elif tc < sc:
            # Back-edge: exit BOTTOM to separate from other back-edges entering TOP
            preferred = (AttachDir.BOTTOM, AttachDir.BOTTOM)
            return preferred, (AttachDir.BOTTOM, AttachDir.TOP)
        else:
            preferred = (AttachDir.BOTTOM, AttachDir.TOP) if tr > sr else (AttachDir.TOP, AttachDir.BOTTOM)

        # Alternative uses vertical
        if tr > sr:
            alt = (AttachDir.BOTTOM, AttachDir.TOP)
        elif tr < sr:
            alt = (AttachDir.TOP, AttachDir.BOTTOM)
        else:
            alt = preferred
    else:
        # Primary flow is top-to-bottom
        if tr > sr:
            preferred = (AttachDir.BOTTOM, AttachDir.TOP)
        elif tr < sr:
            # Back-edge: exit RIGHT to separate from other back-edges entering LEFT
            preferred = (AttachDir.RIGHT, AttachDir.RIGHT)
            return preferred, (AttachDir.RIGHT, AttachDir.LEFT)
        else:
            preferred = (AttachDir.RIGHT, AttachDir.LEFT) if tc > sc else (AttachDir.LEFT, AttachDir.RIGHT)

        # Alternative uses horizontal
        if tc > sc:
            alt = (AttachDir.RIGHT, AttachDir.LEFT)
        elif tc < sc:
            alt = (AttachDir.LEFT, AttachDir.RIGHT)
        else:
            alt = preferred

    return preferred, alt


def _route_edge(
    edge: Edge,
    src: NodePlacement,
    tgt: NodePlacement,
    layout: GridLayout,
    direction: Direction,
    soft_obstacles: set[tuple[int, int]],
) -> RoutedEdge:
    """Route a single edge between two nodes."""
    preferred, alt = _determine_directions(src, tgt, direction)

    # Try preferred path
    # Don't exclude source/target from obstacles — edges must not route
    # through node borders. The pathfinder allows start/end points natively.
    start_pref = _get_attach_point(src, preferred[0])
    end_pref = _get_attach_point(tgt, preferred[1])

    path_pref = find_path(
        start_pref[0], start_pref[1],
        end_pref[0], end_pref[1],
        lambda c, r: layout.is_free(c, r),
        soft_obstacles,
    )

    # Try alternative path
    start_alt = _get_attach_point(src, alt[0])
    end_alt = _get_attach_point(tgt, alt[1])

    path_alt = find_path(
        start_alt[0], start_alt[1],
        end_alt[0], end_alt[1],
        lambda c, r: layout.is_free(c, r),
        soft_obstacles,
    )

    # Pick shorter path
    if path_pref and path_alt:
        if len(path_pref) <= len(path_alt):
            path, start_dir, end_dir = path_pref, preferred[0], preferred[1]
        else:
            path, start_dir, end_dir = path_alt, alt[0], alt[1]
    elif path_pref:
        path, start_dir, end_dir = path_pref, preferred[0], preferred[1]
    elif path_alt:
        path, start_dir, end_dir = path_alt, alt[0], alt[1]
    else:
        # Fallback: direct line
        path = [start_pref, end_pref]
        start_dir, end_dir = preferred

    simplified = simplify_path(path)

    # Convert to drawing coordinates (center of each cell)
    draw_path = [layout.grid_to_draw_center(c, r) for c, r in simplified]

    # Track occupied cells
    occupied = set(path)

    return RoutedEdge(
        edge=edge,
        grid_path=simplified,
        draw_path=draw_path,
        start_dir=start_dir,
        end_dir=end_dir,
        label=edge.label,
        occupied_cells=occupied,
    )


def _route_self_edge(
    edge: Edge,
    src: NodePlacement,
    layout: GridLayout,
    direction: Direction,
) -> RoutedEdge:
    """Route a self-referencing edge (A --> A).

    Self-edge loops out from the top, goes right, comes back down to the right side.
    """
    gc = src.grid

    # Loop: top → above-right → right → back to top-right area
    # Grid path: exit top, go up, go right, go down, enter right side
    path = [
        (gc.col, gc.row - 1),      # top border of node
        (gc.col, gc.row - 2),      # one cell above
        (gc.col + 2, gc.row - 2),  # above and to the right
        (gc.col + 2, gc.row),      # right and level with center
        (gc.col + 1, gc.row),      # right border of node
    ]
    start_dir = AttachDir.TOP
    end_dir = AttachDir.RIGHT

    draw_path = [layout.grid_to_draw_center(c, r) for c, r in path]
    occupied = set(path)

    return RoutedEdge(
        edge=edge,
        grid_path=path,
        draw_path=draw_path,
        start_dir=start_dir,
        end_dir=end_dir,
        label=edge.label,
        occupied_cells=occupied,
    )
