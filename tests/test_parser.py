"""Tests for the mermaid flowchart parser."""
from __future__ import annotations

import pytest

from termaid.parser.flowchart import parse_flowchart
from termaid.graph.model import Direction, EdgeStyle
from termaid.graph.shapes import NodeShape


class TestParseDirection:
    def test_graph_lr(self):
        g = parse_flowchart("graph LR\n  A --> B")
        assert g.direction == Direction.LR

    def test_graph_td(self):
        g = parse_flowchart("graph TD\n  A --> B")
        assert g.direction == Direction.TD

    def test_graph_tb(self):
        g = parse_flowchart("graph TB\n  A --> B")
        assert g.direction == Direction.TB

    def test_graph_bt(self):
        g = parse_flowchart("graph BT\n  A --> B")
        assert g.direction == Direction.BT

    def test_graph_rl(self):
        g = parse_flowchart("graph RL\n  A --> B")
        assert g.direction == Direction.RL

    def test_flowchart_keyword(self):
        g = parse_flowchart("flowchart LR\n  A --> B")
        assert g.direction == Direction.LR
        assert len(g.edges) == 1

    def test_default_direction(self):
        g = parse_flowchart("graph\n  A --> B")
        assert g.direction == Direction.TB


class TestParseNodes:
    def test_plain_node(self):
        g = parse_flowchart("graph LR\n  A")
        assert "A" in g.nodes
        assert g.nodes["A"].label == "A"
        assert g.nodes["A"].shape == NodeShape.RECTANGLE

    def test_rectangle_node(self):
        g = parse_flowchart("graph LR\n  A[Hello World]")
        assert g.nodes["A"].label == "Hello World"
        assert g.nodes["A"].shape == NodeShape.RECTANGLE

    def test_rounded_node(self):
        g = parse_flowchart("graph LR\n  A(Rounded)")
        assert g.nodes["A"].label == "Rounded"
        assert g.nodes["A"].shape == NodeShape.ROUNDED

    def test_stadium_node(self):
        g = parse_flowchart("graph LR\n  A([Stadium])")
        assert g.nodes["A"].label == "Stadium"
        assert g.nodes["A"].shape == NodeShape.STADIUM

    def test_subroutine_node(self):
        g = parse_flowchart("graph LR\n  A[[Subroutine]]")
        assert g.nodes["A"].label == "Subroutine"
        assert g.nodes["A"].shape == NodeShape.SUBROUTINE

    def test_diamond_node(self):
        g = parse_flowchart("graph LR\n  A{Diamond}")
        assert g.nodes["A"].label == "Diamond"
        assert g.nodes["A"].shape == NodeShape.DIAMOND

    def test_hexagon_node(self):
        g = parse_flowchart("graph LR\n  A{{Hexagon}}")
        assert g.nodes["A"].label == "Hexagon"
        assert g.nodes["A"].shape == NodeShape.HEXAGON

    def test_circle_node(self):
        g = parse_flowchart("graph LR\n  A((Circle))")
        assert g.nodes["A"].label == "Circle"
        assert g.nodes["A"].shape == NodeShape.CIRCLE

    def test_double_circle_node(self):
        g = parse_flowchart("graph LR\n  A(((Double)))")
        assert g.nodes["A"].label == "Double"
        assert g.nodes["A"].shape == NodeShape.DOUBLE_CIRCLE

    def test_asymmetric_node(self):
        g = parse_flowchart("graph LR\n  A>Asymmetric]")
        assert g.nodes["A"].label == "Asymmetric"
        assert g.nodes["A"].shape == NodeShape.ASYMMETRIC

    def test_cylinder_node(self):
        g = parse_flowchart("graph LR\n  A[(Database)]")
        assert g.nodes["A"].label == "Database"
        assert g.nodes["A"].shape == NodeShape.CYLINDER

    def test_quoted_label(self):
        g = parse_flowchart('graph LR\n  A["Special (chars)"]')
        assert g.nodes["A"].label == "Special (chars)"

    def test_unicode_label(self):
        g = parse_flowchart('graph LR\n  A["Hello ❤ World"]')
        assert g.nodes["A"].label == "Hello ❤ World"

    def test_multiple_nodes_no_edges(self):
        g = parse_flowchart("graph LR\n  A\n  B\n  C")
        assert len(g.nodes) == 3
        assert g.node_order == ["A", "B", "C"]

    def test_style_class_shorthand(self):
        g = parse_flowchart("graph LR\n  A:::myclass --> B")
        assert g.nodes["A"].style_class == "myclass"

    def test_node_label_update(self):
        """First reference as plain, later with label should update."""
        g = parse_flowchart("graph LR\n  A --> B\n  A[Custom Label]")
        assert g.nodes["A"].label == "Custom Label"


class TestParseEdges:
    def test_solid_arrow(self):
        g = parse_flowchart("graph LR\n  A --> B")
        assert len(g.edges) == 1
        assert g.edges[0].source == "A"
        assert g.edges[0].target == "B"
        assert g.edges[0].style == EdgeStyle.SOLID
        assert g.edges[0].has_arrow_end is True
        assert g.edges[0].has_arrow_start is False

    def test_dotted_arrow(self):
        g = parse_flowchart("graph LR\n  A -.-> B")
        assert len(g.edges) == 1
        assert g.edges[0].style == EdgeStyle.DOTTED

    def test_thick_arrow(self):
        g = parse_flowchart("graph LR\n  A ==> B")
        assert len(g.edges) == 1
        assert g.edges[0].style == EdgeStyle.THICK

    def test_bidirectional(self):
        g = parse_flowchart("graph LR\n  A <--> B")
        assert len(g.edges) == 1
        assert g.edges[0].has_arrow_start is True
        assert g.edges[0].has_arrow_end is True

    def test_labeled_edge_pipe(self):
        g = parse_flowchart("graph LR\n  A -->|yes| B")
        assert len(g.edges) == 1
        assert g.edges[0].label == "yes"

    def test_labeled_edge_text(self):
        g = parse_flowchart("graph LR\n  A -- text --> B")
        assert len(g.edges) == 1
        assert g.edges[0].label == "text"

    def test_chained_arrows(self):
        g = parse_flowchart("graph LR\n  A --> B --> C")
        assert len(g.edges) == 2
        assert g.edges[0].source == "A"
        assert g.edges[0].target == "B"
        assert g.edges[1].source == "B"
        assert g.edges[1].target == "C"

    def test_long_chain(self):
        g = parse_flowchart("graph LR\n  A --> B --> C --> D --> E")
        assert len(g.edges) == 4

    def test_self_reference(self):
        g = parse_flowchart("graph LR\n  A --> A")
        assert len(g.edges) == 1
        assert g.edges[0].is_self_reference is True

    def test_open_link(self):
        g = parse_flowchart("graph LR\n  A --- B")
        assert len(g.edges) == 1
        assert g.edges[0].has_arrow_end is False

    def test_invisible_link(self):
        g = parse_flowchart("graph LR\n  A ~~~ B")
        assert len(g.edges) == 1
        assert g.edges[0].style == EdgeStyle.INVISIBLE


class TestParseAmpersand:
    def test_rhs_ampersand(self):
        g = parse_flowchart("graph LR\n  A --> B & C")
        assert len(g.edges) == 2
        sources = {e.source for e in g.edges}
        targets = {e.target for e in g.edges}
        assert sources == {"A"}
        assert targets == {"B", "C"}

    def test_lhs_ampersand(self):
        g = parse_flowchart("graph LR\n  A & B --> C")
        assert len(g.edges) == 2
        sources = {e.source for e in g.edges}
        targets = {e.target for e in g.edges}
        assert sources == {"A", "B"}
        assert targets == {"C"}

    def test_both_ampersand(self):
        g = parse_flowchart("graph LR\n  A & B --> C & D")
        assert len(g.edges) == 4  # Cartesian product

    def test_ampersand_without_edge(self):
        g = parse_flowchart("graph LR\n  A & B")
        assert len(g.nodes) == 2
        assert len(g.edges) == 0


class TestParseSubgraphs:
    def test_basic_subgraph(self):
        g = parse_flowchart("graph LR\n  subgraph one\n    A --> B\n  end")
        assert len(g.subgraphs) == 1
        assert g.subgraphs[0].id == "one"
        assert "A" in g.subgraphs[0].node_ids
        assert "B" in g.subgraphs[0].node_ids

    def test_subgraph_with_label(self):
        g = parse_flowchart("graph LR\n  subgraph ide1 [My Label]\n    A\n  end")
        assert g.subgraphs[0].id == "ide1"
        assert g.subgraphs[0].label == "My Label"

    def test_nested_subgraphs(self):
        g = parse_flowchart(
            "graph LR\n"
            "  subgraph outer\n"
            "    subgraph inner\n"
            "      A\n"
            "    end\n"
            "  end"
        )
        assert len(g.subgraphs) == 1  # only top-level
        assert len(g.subgraphs[0].children) == 1
        assert g.subgraphs[0].children[0].id == "inner"

    def test_subgraph_direction_override(self):
        g = parse_flowchart(
            "graph LR\n"
            "  subgraph one\n"
            "    direction TB\n"
            "    A --> B\n"
            "  end"
        )
        assert g.subgraphs[0].direction == Direction.TB


class TestParseComments:
    def test_full_line_comment(self):
        g = parse_flowchart("graph LR\n  %% comment\n  A --> B")
        assert len(g.edges) == 1

    def test_inline_comment(self):
        g = parse_flowchart("graph LR\n  A --> B %% inline")
        assert len(g.edges) == 1
        assert "B" in g.nodes

    def test_multiple_comments(self):
        g = parse_flowchart(
            "graph LR\n  %% first\n  A --> B\n  %% second\n  B --> C\n  %% third"
        )
        assert len(g.edges) == 2


class TestParseSemicolons:
    def test_semicolon_separated(self):
        g = parse_flowchart("graph LR\n  A --> B; B --> C; C --> D")
        assert len(g.edges) == 3

    def test_trailing_semicolon(self):
        g = parse_flowchart("graph LR\n  A --> B;")
        assert len(g.edges) == 1


class TestParseClassDef:
    def test_classdef_parsing(self):
        g = parse_flowchart("graph LR\n  A --> B\n  classDef red fill:#f00,stroke:#333")
        assert "red" in g.class_defs
        assert g.class_defs["red"]["fill"] == "#f00"
        assert g.class_defs["red"]["stroke"] == "#333"


class TestParseEdgeCases:
    def test_empty_input(self):
        g = parse_flowchart("")
        assert len(g.nodes) == 0

    def test_header_only(self):
        g = parse_flowchart("graph LR")
        assert len(g.nodes) == 0

    def test_node_id_with_numbers(self):
        g = parse_flowchart("graph LR\n  node1 --> node2")
        assert "node1" in g.nodes
        assert "node2" in g.nodes

    def test_preserves_node_order(self):
        g = parse_flowchart("graph LR\n  C --> A\n  B --> D")
        assert g.node_order == ["C", "A", "B", "D"]

    def test_get_roots(self):
        g = parse_flowchart("graph LR\n  A --> B\n  A --> C\n  B --> D")
        roots = g.get_roots()
        assert roots == ["A"]

    def test_get_roots_multiple(self):
        g = parse_flowchart("graph LR\n  A --> C\n  B --> C")
        roots = g.get_roots()
        assert set(roots) == {"A", "B"}

    def test_thick_label(self):
        g = parse_flowchart("graph LR\n  A == text ==> B")
        assert len(g.edges) == 1
        assert g.edges[0].label == "text"
        assert g.edges[0].style == EdgeStyle.THICK

    def test_dotted_label(self):
        g = parse_flowchart("graph LR\n  A -. text .-> B")
        assert len(g.edges) == 1
        assert g.edges[0].label == "text"
        assert g.edges[0].style == EdgeStyle.DOTTED

    def test_malformed_input_no_crash(self):
        """Malformed input should not crash the parser."""
        g = parse_flowchart("graph LR\n  ???!!!")
        assert isinstance(g.nodes, dict)

    def test_special_chars_in_labels(self):
        g = parse_flowchart('graph LR\n  A["Hello, World! #42"]')
        assert g.nodes["A"].label == "Hello, World! #42"
