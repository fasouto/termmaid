"""Tests for gantt diagram parsing and rendering."""
from __future__ import annotations

from datetime import date

from termaid import render
from termaid.parser.gantt import parse_gantt


# -- Parser tests -------------------------------------------------------------


class TestGanttParser:
    def test_basic_sections_and_tasks(self):
        d = parse_gantt(
            'gantt\n'
            '    title Project Plan\n'
            '    dateFormat YYYY-MM-DD\n'
            '    section Design\n'
            '        Wireframes :des1, 2024-01-01, 2024-01-14\n'
            '    section Development\n'
            '        Frontend :dev1, 2024-01-15, 2024-02-15\n'
        )
        assert d.title == "Project Plan"
        assert len(d.sections) == 2
        assert d.sections[0].title == "Design"
        assert d.sections[1].title == "Development"
        assert d.sections[0].tasks[0].title == "Wireframes"
        assert d.sections[1].tasks[0].title == "Frontend"

    def test_task_tag_done(self):
        d = parse_gantt(
            'gantt\n'
            '    section S\n'
            '        Task A :done, a1, 2024-01-01, 2024-01-10\n'
        )
        task = d.sections[0].tasks[0]
        assert task.is_done is True
        assert task.is_active is False

    def test_task_tag_active(self):
        d = parse_gantt(
            'gantt\n'
            '    section S\n'
            '        Task B :active, b1, 2024-02-01, 2024-02-10\n'
        )
        task = d.sections[0].tasks[0]
        assert task.is_active is True

    def test_task_tag_crit(self):
        d = parse_gantt(
            'gantt\n'
            '    section S\n'
            '        Task C :crit, c1, 2024-03-01, 2024-03-15\n'
        )
        task = d.sections[0].tasks[0]
        assert task.is_crit is True

    def test_task_tag_milestone(self):
        d = parse_gantt(
            'gantt\n'
            '    section S\n'
            '        Release :milestone, m1, 2024-04-01, 2024-04-01\n'
        )
        task = d.sections[0].tasks[0]
        assert task.is_milestone is True

    def test_multiple_tags(self):
        d = parse_gantt(
            'gantt\n'
            '    section S\n'
            '        Urgent :done, crit, u1, 2024-01-01, 2024-01-05\n'
        )
        task = d.sections[0].tasks[0]
        assert task.is_done is True
        assert task.is_crit is True

    def test_after_dependency(self):
        d = parse_gantt(
            'gantt\n'
            '    section S\n'
            '        Task A :a1, 2024-01-01, 2024-01-10\n'
            '        Task B :b1, after a1, 10d\n'
        )
        task_b = d.sections[0].tasks[1]
        assert task_b.after == "a1"
        # After resolution, start should equal end of a1
        assert task_b.start == date(2024, 1, 10)

    def test_duration_days(self):
        d = parse_gantt(
            'gantt\n'
            '    section S\n'
            '        Task :t1, 2024-01-01, 30d\n'
        )
        task = d.sections[0].tasks[0]
        assert task.start == date(2024, 1, 1)
        assert task.end == date(2024, 1, 31)

    def test_duration_weeks(self):
        d = parse_gantt(
            'gantt\n'
            '    section S\n'
            '        Task :t1, 2024-01-01, 2w\n'
        )
        task = d.sections[0].tasks[0]
        assert task.start == date(2024, 1, 1)
        assert task.end == date(2024, 1, 15)

    def test_today_marker_off(self):
        d = parse_gantt(
            'gantt\n'
            '    todayMarker off\n'
            '    section S\n'
            '        Task :t1, 2024-01-01, 2024-01-10\n'
        )
        assert d.today_marker is False

    def test_today_marker_default(self):
        d = parse_gantt(
            'gantt\n'
            '    section S\n'
            '        Task :t1, 2024-01-01, 2024-01-10\n'
        )
        assert d.today_marker is True

    def test_empty_gantt(self):
        d = parse_gantt("gantt")
        assert len(d.sections) == 0
        assert d.title == ""

    def test_comments_ignored(self):
        d = parse_gantt(
            'gantt\n'
            '    %% comment line\n'
            '    section S\n'
            '        Task :t1, 2024-01-01, 2024-01-05\n'
        )
        assert len(d.sections) == 1
        assert len(d.sections[0].tasks) == 1

    def test_task_without_section(self):
        d = parse_gantt(
            'gantt\n'
            '    Task :t1, 2024-01-01, 2024-01-05\n'
        )
        assert len(d.sections) == 1
        assert d.sections[0].title == ""
        assert d.sections[0].tasks[0].title == "Task"


# -- Rendering tests ----------------------------------------------------------


class TestGanttRendering:
    def test_basic_render(self):
        output = render(
            'gantt\n'
            '    title Project Plan\n'
            '    section Design\n'
            '        Wireframes :des1, 2024-01-01, 2024-01-14\n'
            '    section Development\n'
            '        Frontend :dev1, 2024-01-15, 2024-02-15\n'
        )
        assert isinstance(output, str)
        assert len(output) > 0
        assert "Design" in output
        assert "Wireframes" in output
        assert "Development" in output
        assert "Frontend" in output

    def test_title_displayed(self):
        output = render(
            'gantt\n'
            '    title My Schedule\n'
            '    section Work\n'
            '        Coding :c1, 2024-01-01, 2024-01-10\n'
        )
        assert "My Schedule" in output

    def test_render_with_tags(self):
        output = render(
            'gantt\n'
            '    section S\n'
            '        Done task :done, d1, 2024-01-01, 2024-01-05\n'
            '        Active task :active, a1, 2024-01-05, 2024-01-10\n'
        )
        assert "Done" in output
        assert "Active" in output
