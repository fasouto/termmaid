"""Tests for kanban diagram parsing and rendering."""
from __future__ import annotations

from termaid import render
from termaid.parser.kanban import parse_kanban


# -- Parser tests -------------------------------------------------------------


class TestKanbanParser:
    def test_parse_columns(self):
        d = parse_kanban(
            'kanban\n'
            '    Todo\n'
            '        Task A\n'
            '    In Progress\n'
            '        Task B\n'
            '    Done\n'
            '        Task C'
        )
        assert len(d.columns) == 3
        assert d.columns[0].title == "Todo"
        assert d.columns[1].title == "In Progress"
        assert d.columns[2].title == "Done"

    def test_parse_cards_within_columns(self):
        d = parse_kanban(
            'kanban\n'
            '    Todo\n'
            '        Design homepage\n'
            '        Fix login bug\n'
            '    Done\n'
            '        Database setup'
        )
        assert len(d.columns[0].cards) == 2
        assert d.columns[0].cards[0].title == "Design homepage"
        assert d.columns[0].cards[1].title == "Fix login bug"
        assert len(d.columns[1].cards) == 1
        assert d.columns[1].cards[0].title == "Database setup"

    def test_card_with_metadata(self):
        d = parse_kanban(
            'kanban\n'
            '    Todo\n'
            '        Fix bug @alice'
        )
        assert d.columns[0].cards[0].title == "Fix bug"
        assert d.columns[0].cards[0].metadata == "@alice"

    def test_empty_kanban(self):
        d = parse_kanban('kanban')
        assert len(d.columns) == 0

    def test_comments_ignored(self):
        d = parse_kanban(
            'kanban\n'
            '    %% this is a comment\n'
            '    Todo\n'
            '        Task A'
        )
        assert len(d.columns) == 1

    def test_blank_lines_ignored(self):
        d = parse_kanban(
            'kanban\n'
            '\n'
            '    Todo\n'
            '\n'
            '        Task A'
        )
        assert len(d.columns) == 1
        assert len(d.columns[0].cards) == 1

    def test_single_column_no_cards(self):
        d = parse_kanban(
            'kanban\n'
            '    Backlog'
        )
        assert len(d.columns) == 1
        assert d.columns[0].title == "Backlog"
        assert len(d.columns[0].cards) == 0

    def test_multiple_cards_per_column(self):
        d = parse_kanban(
            'kanban\n'
            '    Sprint\n'
            '        Task 1\n'
            '        Task 2\n'
            '        Task 3'
        )
        assert len(d.columns[0].cards) == 3


# -- Rendering tests ----------------------------------------------------------


class TestKanbanRendering:
    def test_basic_render_nonempty(self):
        output = render(
            'kanban\n'
            '    Todo\n'
            '        Task A\n'
            '    Done\n'
            '        Task B'
        )
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_contains_column_names(self):
        output = render(
            'kanban\n'
            '    Todo\n'
            '        Task A\n'
            '    In Progress\n'
            '        Task B\n'
            '    Done\n'
            '        Task C'
        )
        assert "Todo" in output
        assert "In Progress" in output
        assert "Done" in output

    def test_render_contains_card_names(self):
        output = render(
            'kanban\n'
            '    Todo\n'
            '        Fix bug\n'
            '        Add test'
        )
        # Cards may be truncated in narrow columns, so check partial matches
        assert "Fix" in output
        assert "Add" in output

    def test_render_multiple_columns(self):
        output = render(
            'kanban\n'
            '    Backlog\n'
            '        Item 1\n'
            '    Active\n'
            '        Item 2\n'
            '    Complete\n'
            '        Item 3'
        )
        assert "Backlog" in output
        assert "Active" in output
        assert "Complete" in output
