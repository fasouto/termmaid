"""A* pathfinder on the grid coordinate system.

Uses Manhattan distance with +1 corner penalty as heuristic.
4-directional movement only (no diagonals).
Previously-routed edges are soft obstacles (cost +2).
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Callable


@dataclass(order=True)
class _AStarNode:
    f_cost: float
    g_cost: float = field(compare=False)
    col: int = field(compare=False)
    row: int = field(compare=False)
    parent: _AStarNode | None = field(default=None, compare=False, repr=False)


# 4-directional movement
DIRS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right


def heuristic(c1: int, r1: int, c2: int, r2: int) -> float:
    """Manhattan distance with +1 corner penalty when not axis-aligned."""
    dx = abs(c1 - c2)
    dy = abs(r1 - r2)
    if dx == 0 or dy == 0:
        return float(dx + dy)
    return float(dx + dy + 1)  # corner penalty


def find_path(
    start_col: int,
    start_row: int,
    end_col: int,
    end_row: int,
    is_free: Callable[[int, int], bool],
    soft_obstacles: set[tuple[int, int]] | None = None,
    max_iterations: int = 5000,
) -> list[tuple[int, int]] | None:
    """Find a path from start to end using A*.

    Args:
        start_col, start_row: Start grid coordinates
        end_col, end_row: End grid coordinates
        is_free: Function that returns True if a cell is not occupied by a node
        soft_obstacles: Set of cells occupied by previously-routed edges (cost +2)
        max_iterations: Maximum iterations before giving up

    Returns:
        List of (col, row) waypoints, or None if no path found
    """
    if start_col == end_col and start_row == end_row:
        return [(start_col, start_row)]

    soft = soft_obstacles or set()

    start_node = _AStarNode(
        f_cost=heuristic(start_col, start_row, end_col, end_row),
        g_cost=0,
        col=start_col,
        row=start_row,
    )

    open_set: list[_AStarNode] = [start_node]
    closed: set[tuple[int, int]] = set()
    best_g: dict[tuple[int, int], float] = {(start_col, start_row): 0}

    iterations = 0
    while open_set and iterations < max_iterations:
        iterations += 1
        current = heapq.heappop(open_set)

        if current.col == end_col and current.row == end_row:
            return _reconstruct(current)

        key = (current.col, current.row)
        if key in closed:
            continue
        closed.add(key)

        for dc, dr in DIRS:
            nc, nr = current.col + dc, current.row + dr
            nkey = (nc, nr)

            if nkey in closed:
                continue

            # Allow start and end even if "occupied"
            is_endpoint = (nc == end_col and nr == end_row)
            if not is_endpoint and not is_free(nc, nr):
                continue

            # Base cost + soft obstacle penalty
            step_cost = 1.0
            if nkey in soft:
                step_cost += 2.0

            # Corner penalty: if direction changes from parent's direction
            if current.parent is not None:
                prev_dc = current.col - current.parent.col
                prev_dr = current.row - current.parent.row
                if (dc, dr) != (prev_dc, prev_dr):
                    step_cost += 0.5  # slight corner penalty in g-cost too

            new_g = current.g_cost + step_cost

            if nkey in best_g and best_g[nkey] <= new_g:
                continue
            best_g[nkey] = new_g

            h = heuristic(nc, nr, end_col, end_row)
            neighbor = _AStarNode(
                f_cost=new_g + h,
                g_cost=new_g,
                col=nc,
                row=nr,
                parent=current,
            )
            heapq.heappush(open_set, neighbor)

    return None  # No path found


def _reconstruct(node: _AStarNode) -> list[tuple[int, int]]:
    """Reconstruct path from end node to start."""
    path: list[tuple[int, int]] = []
    current: _AStarNode | None = node
    while current is not None:
        path.append((current.col, current.row))
        current = current.parent
    path.reverse()
    return path


def simplify_path(path: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Remove collinear intermediate points, keeping only corners."""
    if len(path) <= 2:
        return path

    result = [path[0]]
    for i in range(1, len(path) - 1):
        prev = path[i - 1]
        curr = path[i]
        nxt = path[i + 1]
        # Keep if direction changes
        d1 = (curr[0] - prev[0], curr[1] - prev[1])
        d2 = (nxt[0] - curr[0], nxt[1] - curr[1])
        if d1 != d2:
            result.append(curr)
    result.append(path[-1])
    return result
