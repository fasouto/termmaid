"""Tests for quadrant chart diagram parsing and rendering."""
from __future__ import annotations

from termaid import render
from termaid.parser.quadrant import parse_quadrant


# -- Parser tests -------------------------------------------------------------


class TestQuadrantParser:
    def test_parse_title(self):
        d = parse_quadrant(
            'quadrantChart\n'
            '    title Effort vs Impact'
        )
        assert d.title == "Effort vs Impact"

    def test_parse_axis_labels(self):
        d = parse_quadrant(
            'quadrantChart\n'
            '    x-axis Low Effort --> High Effort\n'
            '    y-axis Low Impact --> High Impact'
        )
        assert "Low Effort" in d.x_label
        assert "High Effort" in d.x_label
        assert "Low Impact" in d.y_label
        assert "High Impact" in d.y_label

    def test_parse_quadrant_labels(self):
        d = parse_quadrant(
            'quadrantChart\n'
            '    quadrant-1 Do First\n'
            '    quadrant-2 Plan\n'
            '    quadrant-3 Delegate\n'
            '    quadrant-4 Eliminate'
        )
        assert d.quadrant_1 == "Do First"
        assert d.quadrant_2 == "Plan"
        assert d.quadrant_3 == "Delegate"
        assert d.quadrant_4 == "Eliminate"

    def test_parse_data_points(self):
        d = parse_quadrant(
            'quadrantChart\n'
            '    Task A: [0.8, 0.9]\n'
            '    Task B: [0.2, 0.3]'
        )
        assert len(d.points) == 2
        assert d.points[0].label == "Task A"
        assert d.points[0].x == 0.8
        assert d.points[0].y == 0.9
        assert d.points[1].label == "Task B"
        assert d.points[1].x == 0.2
        assert d.points[1].y == 0.3

    def test_default_quadrant_labels(self):
        d = parse_quadrant('quadrantChart')
        assert d.quadrant_1 == "Q1"
        assert d.quadrant_2 == "Q2"
        assert d.quadrant_3 == "Q3"
        assert d.quadrant_4 == "Q4"

    def test_empty_quadrant(self):
        d = parse_quadrant('quadrantChart')
        assert d.title == ""
        assert len(d.points) == 0

    def test_comments_ignored(self):
        d = parse_quadrant(
            'quadrantChart\n'
            '    %% a comment\n'
            '    Task A: [0.5, 0.5]'
        )
        assert len(d.points) == 1

    def test_blank_lines_ignored(self):
        d = parse_quadrant(
            'quadrantChart\n'
            '\n'
            '    title Test\n'
            '\n'
            '    Task A: [0.1, 0.2]'
        )
        assert d.title == "Test"
        assert len(d.points) == 1

    def test_full_chart_parse(self):
        d = parse_quadrant(
            'quadrantChart\n'
            '    title Priority Matrix\n'
            '    x-axis Low Effort --> High Effort\n'
            '    y-axis Low Impact --> High Impact\n'
            '    quadrant-1 Do First\n'
            '    quadrant-2 Plan\n'
            '    quadrant-3 Delegate\n'
            '    quadrant-4 Eliminate\n'
            '    Task A: [0.8, 0.9]\n'
            '    Task B: [0.2, 0.3]\n'
            '    Task C: [0.7, 0.1]'
        )
        assert d.title == "Priority Matrix"
        assert d.quadrant_1 == "Do First"
        assert len(d.points) == 3


# -- Rendering tests ----------------------------------------------------------


class TestQuadrantRendering:
    def test_basic_render_nonempty(self):
        output = render(
            'quadrantChart\n'
            '    title Test Chart\n'
            '    Task A: [0.5, 0.5]'
        )
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_contains_title(self):
        output = render(
            'quadrantChart\n'
            '    title Priority Matrix\n'
            '    Task A: [0.5, 0.5]'
        )
        assert "Priority Matrix" in output

    def test_render_contains_quadrant_labels(self):
        output = render(
            'quadrantChart\n'
            '    quadrant-1 Do First\n'
            '    quadrant-2 Plan\n'
            '    quadrant-3 Delegate\n'
            '    quadrant-4 Eliminate\n'
            '    Task A: [0.5, 0.5]'
        )
        assert "Do First" in output
        assert "Plan" in output
        assert "Delegate" in output
        assert "Eliminate" in output

    def test_render_contains_point_labels(self):
        output = render(
            'quadrantChart\n'
            '    Task Alpha: [0.8, 0.9]\n'
            '    Task Beta: [0.2, 0.3]'
        )
        assert "Task Alpha" in output
        assert "Task Beta" in output

    def test_render_full_chart(self):
        output = render(
            'quadrantChart\n'
            '    title Effort vs Impact\n'
            '    x-axis Low Effort --> High Effort\n'
            '    y-axis Low Impact --> High Impact\n'
            '    quadrant-1 Do First\n'
            '    quadrant-2 Plan\n'
            '    quadrant-3 Delegate\n'
            '    quadrant-4 Eliminate\n'
            '    Task A: [0.8, 0.9]\n'
            '    Task B: [0.2, 0.3]'
        )
        assert "Effort vs Impact" in output
        assert "Task A" in output
        assert "Task B" in output
