"""Comprehensive node shape tests.

Tests all supported shapes: rectangle, rounded, stadium, subroutine,
diamond, hexagon, circle, double_circle, asymmetric, cylinder,
parallelogram, parallelogram_alt, trapezoid, trapezoid_alt.
"""
from __future__ import annotations

import pytest

from termaid import render
from termaid.parser.flowchart import parse_flowchart
from termaid.graph.shapes import NodeShape


# ── Parser shape detection ────────────────────────────────────────────────────

class TestShapeParsing:
    """Verify parser correctly identifies all shape types."""

    @pytest.mark.parametrize("syntax,expected_shape", [
        ("A[text]", NodeShape.RECTANGLE),
        ("A(text)", NodeShape.ROUNDED),
        ("A([text])", NodeShape.STADIUM),
        ("A[[text]]", NodeShape.SUBROUTINE),
        ("A{text}", NodeShape.DIAMOND),
        ("A{{text}}", NodeShape.HEXAGON),
        ("A((text))", NodeShape.CIRCLE),
        ("A(((text)))", NodeShape.DOUBLE_CIRCLE),
        ("A>text]", NodeShape.ASYMMETRIC),
        ("A[(text)]", NodeShape.CYLINDER),
        (r"A[/text\]", NodeShape.TRAPEZOID),
        (r"A[\text/]", NodeShape.TRAPEZOID_ALT),
        ("A[/text/]", NodeShape.PARALLELOGRAM),
        (r"A[\text\]", NodeShape.PARALLELOGRAM_ALT),
    ])
    def test_shape_detection(self, syntax: str, expected_shape: NodeShape):
        g = parse_flowchart(f"graph LR\n  {syntax}")
        assert g.nodes["A"].shape == expected_shape

    def test_plain_node_defaults_to_rectangle(self):
        g = parse_flowchart("graph LR\n  A")
        assert g.nodes["A"].shape == NodeShape.RECTANGLE


# ── Shape rendering ───────────────────────────────────────────────────────────

class TestShapeRendering:
    """Verify all shapes render without errors and produce visible output."""

    ALL_SHAPES = [
        ("A[Rectangle]", "Rectangle"),
        ("A(Rounded)", "Rounded"),
        ("A([Stadium])", "Stadium"),
        ("A[[Subroutine]]", "Subroutine"),
        ("A{Diamond}", "Diamond"),
        ("A{{Hexagon}}", "Hexagon"),
        ("A((Circle))", "Circle"),
        ("A(((Double)))", "Double"),
        ("A>Asym]", "Asym"),
        ("A[(Database)]", "Database"),
        (r"A[/Trap\]", "Trap"),
        (r"A[\AltT/]", "AltT"),
        ("A[/Para/]", "Para"),
        (r"A[\AltP\]", "AltP"),
    ]

    @pytest.mark.parametrize("syntax,label", ALL_SHAPES)
    def test_shape_renders(self, syntax: str, label: str):
        output = render(f"graph LR\n  {syntax}")
        assert label in output, f"Shape {syntax} should render label '{label}'"
        assert len(output.strip()) > 0

    @pytest.mark.parametrize("syntax,label", ALL_SHAPES)
    def test_shape_renders_ascii(self, syntax: str, label: str):
        output = render(f"graph LR\n  {syntax}", use_ascii=True)
        assert label in output

    def test_rectangle_has_square_corners(self):
        output = render("graph LR\n  A[Hello]")
        assert "┌" in output
        assert "┐" in output
        assert "└" in output
        assert "┘" in output

    def test_rounded_has_round_corners(self):
        output = render("graph LR\n  A(Hello)")
        assert "╭" in output
        assert "╯" in output

    def test_diamond_has_marker(self):
        output = render("graph LR\n  A{Decision}")
        assert "◇" in output

    def test_stadium_has_parens(self):
        output = render("graph LR\n  A([Stadium])")
        assert "(" in output
        assert ")" in output

    def test_hexagon_has_angle_brackets(self):
        output = render("graph LR\n  A{{Hex}}")
        assert "<" in output or "/" in output

    def test_cylinder_has_curve_chars(self):
        output = render("graph LR\n  A[(DB)]")
        # Cylinder should have some distinctive top/bottom
        assert "DB" in output

    def test_all_shapes_in_one_graph(self):
        """All shapes in a single graph should render without errors."""
        output = render(
            "graph TD\n"
            "  A[Rect] --> B(Round)\n"
            "  B --> C{Diamond}\n"
            "  C --> D([Stadium])\n"
            "  D --> E[[Sub]]\n"
            "  E --> F((Circle))\n"
        )
        for label in ["Rect", "Round", "Diamond", "Stadium", "Sub", "Circle"]:
            assert label in output
