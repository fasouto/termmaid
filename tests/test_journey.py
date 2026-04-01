"""Tests for user journey diagram parsing and rendering."""
from __future__ import annotations

from termaid import render
from termaid.parser.journey import parse_journey


# -- Parser tests -------------------------------------------------------------


class TestJourneyParser:
    def test_basic_sections_and_tasks(self):
        d = parse_journey(
            'journey\n'
            '    title My working day\n'
            '    section Go to work\n'
            '        Make tea: 5: Me\n'
            '        Go upstairs: 3: Me\n'
            '    section Go home\n'
            '        Sit down: 5: Me\n'
        )
        assert d.title == "My working day"
        assert len(d.sections) == 2
        assert d.sections[0].title == "Go to work"
        assert d.sections[1].title == "Go home"
        assert len(d.sections[0].tasks) == 2
        assert len(d.sections[1].tasks) == 1

    def test_task_scores(self):
        d = parse_journey(
            'journey\n'
            '    section S\n'
            '        Happy task: 5: Me\n'
            '        Neutral task: 3: Me\n'
            '        Sad task: 1: Me\n'
        )
        assert d.sections[0].tasks[0].score == 5
        assert d.sections[0].tasks[1].score == 3
        assert d.sections[0].tasks[2].score == 1

    def test_score_clamped_high(self):
        d = parse_journey(
            'journey\n'
            '    section S\n'
            '        Too high: 9: Me\n'
        )
        assert d.sections[0].tasks[0].score == 5

    def test_score_clamped_low(self):
        d = parse_journey(
            'journey\n'
            '    section S\n'
            '        Too low: -1: Me\n'
        )
        assert d.sections[0].tasks[0].score == 1

    def test_multiple_actors(self):
        d = parse_journey(
            'journey\n'
            '    section S\n'
            '        Team work: 4: Alice, Bob, Charlie\n'
        )
        task = d.sections[0].tasks[0]
        assert task.actors == ["Alice", "Bob", "Charlie"]

    def test_single_actor(self):
        d = parse_journey(
            'journey\n'
            '    section S\n'
            '        Solo: 5: Me\n'
        )
        assert d.sections[0].tasks[0].actors == ["Me"]

    def test_title(self):
        d = parse_journey(
            'journey\n'
            '    title Customer Onboarding\n'
            '    section Step 1\n'
            '        Sign up: 4: User\n'
        )
        assert d.title == "Customer Onboarding"

    def test_no_title(self):
        d = parse_journey(
            'journey\n'
            '    section S\n'
            '        Task: 3: Me\n'
        )
        assert d.title == ""

    def test_empty_journey(self):
        d = parse_journey("journey")
        assert len(d.sections) == 0
        assert d.title == ""

    def test_comments_ignored(self):
        d = parse_journey(
            'journey\n'
            '    %% this is a comment\n'
            '    section S\n'
            '        Task: 3: Me\n'
        )
        assert len(d.sections) == 1

    def test_task_without_section(self):
        d = parse_journey(
            'journey\n'
            '    Do something: 4: Me\n'
        )
        assert len(d.sections) == 1
        assert d.sections[0].title == ""
        assert d.sections[0].tasks[0].title == "Do something"

    def test_blank_lines_ignored(self):
        d = parse_journey(
            'journey\n'
            '\n'
            '    section S\n'
            '\n'
            '        Task: 3: Me\n'
            '\n'
        )
        assert len(d.sections) == 1
        assert len(d.sections[0].tasks) == 1


# -- Rendering tests ----------------------------------------------------------


class TestJourneyRendering:
    def test_basic_render(self):
        output = render(
            'journey\n'
            '    title My working day\n'
            '    section Go to work\n'
            '        Make tea: 5: Me\n'
            '        Go upstairs: 3: Me\n'
            '    section Go home\n'
            '        Sit down: 5: Me\n'
        )
        assert isinstance(output, str)
        assert len(output) > 0
        assert "Make tea" in output
        assert "Go upstairs" in output
        assert "Sit down" in output

    def test_title_displayed(self):
        output = render(
            'journey\n'
            '    title Customer Flow\n'
            '    section Visit\n'
            '        Browse: 4: User\n'
        )
        assert "Customer Flow" in output

    def test_section_names_displayed(self):
        output = render(
            'journey\n'
            '    section Morning\n'
            '        Coffee: 5: Me\n'
            '    section Afternoon\n'
            '        Meetings: 2: Me\n'
        )
        assert "Morning" in output
        assert "Afternoon" in output

    def test_actors_displayed(self):
        output = render(
            'journey\n'
            '    section S\n'
            '        Collaborate: 4: Alice, Bob\n'
        )
        assert "Alice" in output
        assert "Bob" in output
