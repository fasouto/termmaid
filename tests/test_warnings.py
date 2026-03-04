"""Tests for the warnings system and error handling."""
from __future__ import annotations

from termaid import render
from termaid.parser.sequence import parse_sequence_diagram
from termaid.parser.classdiagram import parse_class_diagram
from termaid.parser.erdiagram import parse_er_diagram
from termaid.parser.gitgraph import parse_git_graph


class TestWarnings:
    def test_sequence_unrecognized_line_warns(self):
        d = parse_sequence_diagram(
            "sequenceDiagram\n"
            "  Alice->>Bob: Hello\n"
            "  !!!bogus line!!!"
        )
        assert len(d.warnings) == 1
        assert "Unrecognized line" in d.warnings[0]
        assert "!!!bogus line!!!" in d.warnings[0]

    def test_sequence_valid_input_no_warnings(self):
        d = parse_sequence_diagram(
            "sequenceDiagram\n"
            "  participant A as Alice\n"
            "  A->>B: Hello\n"
            "  B-->>A: Hi"
        )
        assert d.warnings == []

    def test_sequence_skip_lines_no_warning(self):
        """Control flow keywords (alt, loop, end, etc.) should not generate warnings."""
        d = parse_sequence_diagram(
            "sequenceDiagram\n"
            "  Alice->>Bob: Hello\n"
            "  alt success\n"
            "  Bob-->>Alice: OK\n"
            "  else failure\n"
            "  Bob-->>Alice: Error\n"
            "  end"
        )
        assert d.warnings == []

    def test_classdiagram_unrecognized_line_warns(self):
        d = parse_class_diagram(
            "classDiagram\n"
            "  class Foo\n"
            "  !!!bogus!!!"
        )
        assert any("Unrecognized line" in w for w in d.warnings)

    def test_erdiagram_unrecognized_line_warns(self):
        d = parse_er_diagram(
            "erDiagram\n"
            "  CUSTOMER ||--o{ ORDER : places\n"
            "  !!!bogus!!!"
        )
        assert any("Unrecognized line" in w for w in d.warnings)

    def test_gitgraph_checkout_nonexistent_branch_warns(self):
        d = parse_git_graph(
            "gitGraph\n"
            "  commit\n"
            "  checkout nonexistent"
        )
        assert any("non-existent branch" in w.lower() for w in d.warnings)

    def test_gitgraph_cherry_pick_nonexistent_commit_warns(self):
        d = parse_git_graph(
            "gitGraph\n"
            "  commit\n"
            '  cherry-pick id: "doesnotexist"'
        )
        assert any("non-existent commit" in w.lower() for w in d.warnings)

    def test_classdiagram_style_directive_warns(self):
        d = parse_class_diagram(
            "classDiagram\n"
            "  class Foo\n"
            "  classDef highlight fill:#f9f\n"
            "  style Foo highlight"
        )
        assert len([w for w in d.warnings if "Unsupported directive" in w]) == 2

    def test_gitgraph_reset_unknown_ref_warns(self):
        d = parse_git_graph("gitGraph\n  commit\n  reset nonexistent")
        assert any("unknown ref" in w.lower() for w in d.warnings)

    def test_gitgraph_valid_reset_no_warnings(self):
        d = parse_git_graph(
            "gitGraph\n  commit\n  branch dev\n  commit\n  checkout main\n  reset dev\n  commit"
        )
        assert d.warnings == []

    def test_gitgraph_valid_no_warnings(self):
        d = parse_git_graph(
            "gitGraph\n"
            "  commit\n"
            "  branch dev\n"
            "  commit\n"
            "  checkout main\n"
            "  commit"
        )
        assert d.warnings == []


class TestErrorHandling:
    def test_render_does_not_crash_on_garbage(self):
        result = render("this is not valid mermaid at all 🗑️")
        assert isinstance(result, str)

    def test_render_does_not_crash_on_empty(self):
        result = render("")
        assert isinstance(result, str)

    def test_render_error_message_on_bad_input(self):
        """render() should return a friendly error string if it would crash."""
        # This tests that even if internal code raises, we get a string back
        result = render("sequenceDiagram")
        assert isinstance(result, str)
