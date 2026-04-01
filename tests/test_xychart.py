"""Tests for XY chart diagram parsing and rendering."""
from __future__ import annotations

from termaid import render
from termaid.parser.xychart import parse_xychart


# -- Parser tests -------------------------------------------------------------


class TestXYChartParser:
    def test_bar_chart(self):
        d = parse_xychart(
            'xychart-beta\n'
            '    x-axis [Q1, Q2, Q3, Q4]\n'
            '    bar [10, 25, 18, 32]\n'
        )
        assert len(d.datasets) == 1
        assert d.datasets[0].chart_type == "bar"
        assert d.datasets[0].values == [10, 25, 18, 32]
        assert d.x_categories == ["Q1", "Q2", "Q3", "Q4"]

    def test_line_chart(self):
        d = parse_xychart(
            'xychart-beta\n'
            '    x-axis [Jan, Feb, Mar]\n'
            '    line [5, 12, 8]\n'
        )
        assert len(d.datasets) == 1
        assert d.datasets[0].chart_type == "line"
        assert d.datasets[0].values == [5, 12, 8]

    def test_combo_bar_and_line(self):
        d = parse_xychart(
            'xychart-beta\n'
            '    x-axis [A, B, C]\n'
            '    bar [10, 20, 30]\n'
            '    line [5, 15, 25]\n'
        )
        assert len(d.datasets) == 2
        assert d.datasets[0].chart_type == "bar"
        assert d.datasets[1].chart_type == "line"

    def test_horizontal_mode(self):
        d = parse_xychart(
            'xychart-beta horizontal\n'
            '    x-axis [A, B]\n'
            '    bar [10, 20]\n'
        )
        assert d.horizontal is True

    def test_vertical_default(self):
        d = parse_xychart(
            'xychart-beta\n'
            '    bar [1, 2]\n'
        )
        assert d.horizontal is False

    def test_title(self):
        d = parse_xychart(
            'xychart-beta\n'
            '    title "Revenue Report"\n'
            '    bar [10, 20]\n'
        )
        assert d.title == "Revenue Report"

    def test_x_axis_label(self):
        d = parse_xychart(
            'xychart-beta\n'
            '    x-axis "Month" [Jan, Feb, Mar]\n'
            '    bar [10, 20, 30]\n'
        )
        assert d.x_label == "Month"
        assert d.x_categories == ["Jan", "Feb", "Mar"]

    def test_y_axis_label(self):
        d = parse_xychart(
            'xychart-beta\n'
            '    y-axis "Revenue (M)"\n'
            '    bar [10, 20]\n'
        )
        assert d.y_label == "Revenue (M)"

    def test_y_axis_range(self):
        d = parse_xychart(
            'xychart-beta\n'
            '    y-axis "Value" 0 --> 50\n'
            '    bar [10, 20]\n'
        )
        assert d.y_label == "Value"
        assert d.y_range == (0, 50)

    def test_x_axis_range(self):
        d = parse_xychart(
            'xychart-beta\n'
            '    x-axis "Score" 0 --> 100\n'
            '    bar [10, 20]\n'
        )
        assert d.x_label == "Score"
        assert d.x_range == (0, 100)

    def test_empty_chart(self):
        d = parse_xychart("xychart-beta")
        assert len(d.datasets) == 0
        assert d.title == ""

    def test_comments_ignored(self):
        d = parse_xychart(
            'xychart-beta\n'
            '    %% a comment\n'
            '    bar [10, 20]\n'
        )
        assert len(d.datasets) == 1


# -- Rendering tests ----------------------------------------------------------


class TestXYChartRendering:
    def test_bar_chart_render(self):
        output = render(
            'xychart-beta\n'
            '    x-axis [Q1, Q2, Q3, Q4]\n'
            '    bar [10, 25, 18, 32]\n'
        )
        assert isinstance(output, str)
        assert len(output) > 0
        assert "Q1" in output
        assert "Q4" in output

    def test_title_displayed(self):
        output = render(
            'xychart-beta\n'
            '    title "Sales Data"\n'
            '    x-axis [Jan, Feb]\n'
            '    bar [100, 200]\n'
        )
        assert "Sales Data" in output

    def test_line_chart_render(self):
        output = render(
            'xychart-beta\n'
            '    x-axis [A, B, C]\n'
            '    line [5, 15, 10]\n'
        )
        assert isinstance(output, str)
        assert len(output) > 0

    def test_combo_render(self):
        output = render(
            'xychart-beta\n'
            '    x-axis [X, Y, Z]\n'
            '    bar [10, 20, 30]\n'
            '    line [8, 18, 28]\n'
        )
        assert isinstance(output, str)
        assert len(output) > 0
        assert "X" in output
