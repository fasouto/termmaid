"""Tests for edge routing (A* pathfinding and direction selection)."""
from __future__ import annotations

import pytest

from termaid.parser.flowchart import parse_flowchart
from termaid.layout.grid import compute_layout
from termaid.routing.router import route_edges, RoutedEdge
from termaid.routing.pathfinder import find_path, simplify_path, heuristic


class TestHeuristic:
    def test_same_point(self):
        assert heuristic(0, 0, 0, 0) == 0.0

    def test_horizontal(self):
        assert heuristic(0, 0, 5, 0) == 5.0

    def test_vertical(self):
        assert heuristic(0, 0, 0, 5) == 5.0

    def test_diagonal_penalty(self):
        # Manhattan distance is 10, but +1 corner penalty
        assert heuristic(0, 0, 5, 5) == 11.0


class TestPathfinder:
    def test_straight_path(self):
        path = find_path(0, 0, 5, 0, lambda c, r: True)
        assert path is not None
        assert path[0] == (0, 0)
        assert path[-1] == (5, 0)

    def test_path_around_obstacle(self):
        # Obstacle at (2, 0)
        def is_free(c, r):
            return not (c == 2 and r == 0)

        path = find_path(0, 0, 4, 0, is_free)
        assert path is not None
        assert (2, 0) not in path
        assert path[0] == (0, 0)
        assert path[-1] == (4, 0)

    def test_no_path(self):
        # Completely walled off
        def is_free(c, r):
            return c == 0 and r == 0

        path = find_path(0, 0, 5, 5, is_free)
        assert path is None

    def test_adjacent_cells(self):
        path = find_path(0, 0, 1, 0, lambda c, r: True)
        assert path == [(0, 0), (1, 0)]


class TestSimplifyPath:
    def test_already_simple(self):
        assert simplify_path([(0, 0), (5, 0)]) == [(0, 0), (5, 0)]

    def test_straight_line(self):
        path = [(0, 0), (1, 0), (2, 0), (3, 0)]
        assert simplify_path(path) == [(0, 0), (3, 0)]

    def test_one_corner(self):
        path = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)]
        result = simplify_path(path)
        assert result == [(0, 0), (2, 0), (2, 2)]

    def test_two_corners(self):
        path = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (4, 2)]
        result = simplify_path(path)
        assert result == [(0, 0), (2, 0), (2, 2), (4, 2)]


class TestEdgeRouting:
    def test_simple_lr_routing(self):
        g = parse_flowchart("graph LR\n  A --> B")
        layout = compute_layout(g)
        routed = route_edges(g, layout)
        assert len(routed) == 1
        re = routed[0]
        assert re.edge.source == "A"
        assert re.edge.target == "B"
        assert len(re.draw_path) >= 2

    def test_all_edges_routed(self):
        g = parse_flowchart("graph LR\n  A --> B\n  A --> C\n  B --> D")
        layout = compute_layout(g)
        routed = route_edges(g, layout)
        assert len(routed) == 3

    def test_self_reference_routing(self):
        g = parse_flowchart("graph LR\n  A --> A")
        layout = compute_layout(g)
        routed = route_edges(g, layout)
        assert len(routed) == 1
        re = routed[0]
        assert len(re.draw_path) >= 3  # Self-loop has multiple points

    def test_no_edge_through_node(self):
        """Edges should not route through node interiors."""
        g = parse_flowchart("graph LR\n  A --> B\n  A --> C\n  B --> D\n  C --> D")
        layout = compute_layout(g)
        routed = route_edges(g, layout)

        # Collect all node grid cells
        node_cells: dict[tuple[int, int], str] = {}
        for nid, p in layout.placements.items():
            for dc in range(-1, 2):
                for dr in range(-1, 2):
                    node_cells[(p.grid.col + dc, p.grid.row + dr)] = nid

        for re in routed:
            for col, row in re.grid_path[1:-1]:  # Skip start and end
                if (col, row) in node_cells:
                    owner = node_cells[(col, row)]
                    # This cell belongs to a node, but it should only be the source or target
                    assert owner in (re.edge.source, re.edge.target), (
                        f"Edge {re.edge.source}->{re.edge.target} routes through "
                        f"node {owner} at ({col}, {row})"
                    )

    def test_draw_path_coordinates_valid(self):
        """Draw path coordinates should be non-negative."""
        g = parse_flowchart("graph LR\n  A --> B --> C")
        layout = compute_layout(g)
        routed = route_edges(g, layout)
        for re in routed:
            for x, y in re.draw_path:
                assert x >= 0, f"Negative x in path: {x}"
                assert y >= 0, f"Negative y in path: {y}"

    def test_soft_obstacles_prevent_overlap(self):
        """Edges routed later should prefer paths that don't overlap earlier edges."""
        g = parse_flowchart("graph LR\n  A --> C\n  B --> D\n  A --> D\n  B --> C")
        layout = compute_layout(g)
        routed = route_edges(g, layout)
        # Check that at least some edges have different paths
        paths = [tuple(re.grid_path) for re in routed]
        # Not all paths should be identical
        assert len(set(paths)) > 1
