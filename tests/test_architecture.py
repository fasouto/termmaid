"""Tests for architecture diagram parsing and rendering."""
from __future__ import annotations

from termaid import render
from termaid.parser.architecture import parse_architecture, _compute_grid_positions


# -- Parser tests -------------------------------------------------------------


class TestArchitectureParser:
    def test_basic_group_and_service(self):
        g = parse_architecture(
            'architecture-beta\n'
            '    group api(cloud)[API]\n'
            '    service db(database)[Database] in api\n'
        )
        assert len(g.subgraphs) == 1
        assert g.subgraphs[0].label == "API"
        assert "db" in g.nodes
        assert "Database" in g.nodes["db"].label

    def test_service_with_icon(self):
        g = parse_architecture(
            'architecture-beta\n'
            '    service srv(server)[My Server]\n'
        )
        node = g.nodes["srv"]
        assert "My Server" in node.label

    def test_service_without_icon(self):
        g = parse_architecture(
            'architecture-beta\n'
            '    service plain[Plain Service]\n'
        )
        node = g.nodes["plain"]
        assert node.label == "Plain Service"

    def test_multiple_services_in_group(self):
        g = parse_architecture(
            'architecture-beta\n'
            '    group g1(cloud)[Group One]\n'
            '    service s1(server)[Service 1] in g1\n'
            '    service s2(database)[Service 2] in g1\n'
        )
        assert len(g.subgraphs[0].node_ids) == 2
        assert "s1" in g.subgraphs[0].node_ids
        assert "s2" in g.subgraphs[0].node_ids

    def test_edge_with_directions(self):
        g = parse_architecture(
            'architecture-beta\n'
            '    service a(server)[A]\n'
            '    service b(server)[B]\n'
            '    a:R --> L:b\n'
        )
        assert len(g.edges) == 1
        assert g.edges[0].source == "a"
        assert g.edges[0].target == "b"

    def test_edge_arrow_directions(self):
        g = parse_architecture(
            'architecture-beta\n'
            '    service x(server)[X]\n'
            '    service y(server)[Y]\n'
            '    x:R --> L:y\n'
        )
        edge = g.edges[0]
        assert edge.has_arrow_end is True
        assert edge.has_arrow_start is False

    def test_edge_bidirectional(self):
        g = parse_architecture(
            'architecture-beta\n'
            '    service x(server)[X]\n'
            '    service y(server)[Y]\n'
            '    x:R <--> L:y\n'
        )
        edge = g.edges[0]
        assert edge.has_arrow_start is True
        assert edge.has_arrow_end is True

    def test_junction(self):
        g = parse_architecture(
            'architecture-beta\n'
            '    group g1(cloud)[G]\n'
            '    junction j1 in g1\n'
        )
        assert "j1" in g.nodes

    def test_in_group_nesting(self):
        g = parse_architecture(
            'architecture-beta\n'
            '    group outer(cloud)[Outer]\n'
            '    group inner(cloud)[Inner] in outer\n'
            '    service s1(server)[S1] in inner\n'
        )
        assert len(g.subgraphs) == 1  # outer is top-level
        assert g.subgraphs[0].label == "Outer"
        # inner is nested inside outer
        assert len(g.subgraphs[0].children) == 1
        assert g.subgraphs[0].children[0].label == "Inner"

    def test_empty_architecture(self):
        g = parse_architecture("architecture-beta")
        assert len(g.nodes) == 0
        assert len(g.edges) == 0


class TestGridPositionComputation:
    def test_basic_lr_positions(self):
        node_ids = ["a", "b"]
        hints = [("a", "R", "b", "L")]
        pos = _compute_grid_positions(node_ids, hints)
        # b should be to the right of a
        assert pos["b"][0] > pos["a"][0]

    def test_basic_tb_positions(self):
        node_ids = ["a", "b"]
        hints = [("a", "B", "b", "T")]
        pos = _compute_grid_positions(node_ids, hints)
        # b should be below a
        assert pos["b"][1] > pos["a"][1]

    def test_chain_positions(self):
        node_ids = ["a", "b", "c"]
        hints = [("a", "R", "b", "L"), ("b", "R", "c", "L")]
        pos = _compute_grid_positions(node_ids, hints)
        assert pos["a"][0] < pos["b"][0] < pos["c"][0]

    def test_unconnected_nodes_placed(self):
        node_ids = ["a", "b", "c"]
        hints = [("a", "R", "b", "L")]
        pos = _compute_grid_positions(node_ids, hints)
        assert "c" in pos  # c should still get a position


# -- Rendering tests ----------------------------------------------------------


class TestArchitectureRendering:
    def test_basic_render(self):
        output = render(
            'architecture-beta\n'
            '    group api(cloud)[API]\n'
            '    service db(database)[Database] in api\n'
            '    service server(server)[Server] in api\n'
            '    db:R --> L:server\n'
        )
        assert isinstance(output, str)
        assert len(output) > 0
        assert "Database" in output
        assert "Server" in output

    def test_render_with_groups(self):
        output = render(
            'architecture-beta\n'
            '    group cloud(cloud)[Cloud Infra]\n'
            '    service web(server)[Web App] in cloud\n'
            '    service store(database)[Data Store] in cloud\n'
            '    web:R --> L:store\n'
        )
        assert "Cloud Infra" in output
        assert "Web App" in output
        assert "Data Store" in output
