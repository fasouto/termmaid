"""Tests for timeline diagram parsing and rendering."""
from __future__ import annotations

from termaid import render
from termaid.parser.timeline import parse_timeline


# -- Parser tests -------------------------------------------------------------


class TestTimelineParser:
    def test_parse_title(self):
        d = parse_timeline(
            'timeline\n'
            '    title My Project\n'
            '    section Phase 1\n'
            '        Design : Wireframes'
        )
        assert d.title == "My Project"

    def test_parse_sections(self):
        d = parse_timeline(
            'timeline\n'
            '    section Phase 1\n'
            '        Design : Wireframes\n'
            '    section Phase 2\n'
            '        Build : Frontend'
        )
        assert len(d.sections) == 2
        assert d.sections[0].title == "Phase 1"
        assert d.sections[1].title == "Phase 2"

    def test_parse_events_in_section(self):
        d = parse_timeline(
            'timeline\n'
            '    section Phase 1\n'
            '        Design : Wireframes, Mockups\n'
            '        Review : Stakeholder sign-off'
        )
        assert len(d.sections[0].events) == 2
        assert d.sections[0].events[0].title == "Design"
        assert d.sections[0].events[1].title == "Review"

    def test_parse_event_details(self):
        d = parse_timeline(
            'timeline\n'
            '    section Build\n'
            '        Coding : Frontend, Backend, API'
        )
        event = d.sections[0].events[0]
        assert event.title == "Coding"
        assert event.details == ["Frontend", "Backend", "API"]

    def test_event_without_details(self):
        d = parse_timeline(
            'timeline\n'
            '    section Phase 1\n'
            '        Kickoff'
        )
        event = d.sections[0].events[0]
        assert event.title == "Kickoff"
        assert event.details == []

    def test_events_without_section_creates_default(self):
        d = parse_timeline(
            'timeline\n'
            '    Event One\n'
            '    Event Two'
        )
        assert len(d.sections) == 1
        assert d.sections[0].title == ""
        assert len(d.sections[0].events) == 2

    def test_empty_timeline(self):
        d = parse_timeline('timeline')
        assert d.title == ""
        assert len(d.sections) == 0

    def test_comments_ignored(self):
        d = parse_timeline(
            'timeline\n'
            '    %% a comment\n'
            '    section Work\n'
            '        Task : Detail'
        )
        assert len(d.sections) == 1

    def test_blank_lines_ignored(self):
        d = parse_timeline(
            'timeline\n'
            '\n'
            '    section Work\n'
            '\n'
            '        Task : Detail'
        )
        assert len(d.sections) == 1
        assert len(d.sections[0].events) == 1


# -- Rendering tests ----------------------------------------------------------


class TestTimelineRendering:
    def test_basic_render_nonempty(self):
        output = render(
            'timeline\n'
            '    title Project Plan\n'
            '    section Phase 1\n'
            '        Design : Wireframes'
        )
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_contains_title(self):
        output = render(
            'timeline\n'
            '    title Release Schedule\n'
            '    section Q1\n'
            '        Planning : Scope'
        )
        assert "Release Schedule" in output

    def test_render_contains_sections_and_events(self):
        output = render(
            'timeline\n'
            '    section Phase 1\n'
            '        Design : Wireframes\n'
            '    section Phase 2\n'
            '        Build : Frontend'
        )
        assert "Phase 1" in output
        assert "Phase 2" in output
        assert "Design" in output
        assert "Build" in output

    def test_render_contains_event_details(self):
        output = render(
            'timeline\n'
            '    section Work\n'
            '        Coding : Frontend, Backend'
        )
        assert "Frontend" in output
        assert "Backend" in output
