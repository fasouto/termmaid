"""Tests for packet diagram parsing and rendering."""
from __future__ import annotations

from termaid import render
from termaid.parser.packet import parse_packet


# -- Parser tests -------------------------------------------------------------


class TestPacketParser:
    def test_basic_fields(self):
        d = parse_packet(
            'packet-beta\n'
            '    0-15: "Source Port"\n'
            '    16-31: "Destination Port"'
        )
        assert len(d.fields) == 2
        assert d.fields[0].label == "Source Port"
        assert d.fields[1].label == "Destination Port"

    def test_field_bit_ranges(self):
        d = parse_packet(
            'packet-beta\n'
            '    0-15: "Source Port"\n'
            '    16-31: "Destination Port"\n'
            '    32-63: "Sequence Number"'
        )
        assert d.fields[0].start == 0
        assert d.fields[0].end == 15
        assert d.fields[1].start == 16
        assert d.fields[1].end == 31
        assert d.fields[2].start == 32
        assert d.fields[2].end == 63

    def test_field_bits_property(self):
        d = parse_packet(
            'packet-beta\n'
            '    0-15: "Source Port"\n'
            '    32-63: "Sequence Number"'
        )
        assert d.fields[0].bits == 16
        assert d.fields[1].bits == 32

    def test_field_labels(self):
        d = parse_packet(
            'packet-beta\n'
            '    0-3: "Version"\n'
            '    4-7: "IHL"\n'
            '    8-15: "Type of Service"'
        )
        assert d.fields[0].label == "Version"
        assert d.fields[1].label == "IHL"
        assert d.fields[2].label == "Type of Service"

    def test_auto_increment_syntax(self):
        d = parse_packet(
            'packet-beta\n'
            '    +16: "Source Port"\n'
            '    +16: "Destination Port"'
        )
        assert d.fields[0].start == 0
        assert d.fields[0].end == 15
        assert d.fields[1].start == 16
        assert d.fields[1].end == 31

    def test_single_bit_field(self):
        d = parse_packet(
            'packet-beta\n'
            '    0: "Flag"'
        )
        assert d.fields[0].start == 0
        assert d.fields[0].end == 0
        assert d.fields[0].bits == 1

    def test_empty_packet(self):
        d = parse_packet('packet-beta')
        assert len(d.fields) == 0

    def test_comments_ignored(self):
        d = parse_packet(
            'packet-beta\n'
            '    %% this is a comment\n'
            '    0-15: "Source Port"'
        )
        assert len(d.fields) == 1

    def test_blank_lines_ignored(self):
        d = parse_packet(
            'packet-beta\n'
            '\n'
            '    0-15: "Source Port"\n'
            '\n'
            '    16-31: "Destination Port"'
        )
        assert len(d.fields) == 2

    def test_unquoted_labels(self):
        d = parse_packet(
            'packet-beta\n'
            '    0-15: Source Port'
        )
        assert d.fields[0].label == "Source Port"


# -- Rendering tests ----------------------------------------------------------


class TestPacketRendering:
    def test_basic_render_nonempty(self):
        output = render(
            'packet-beta\n'
            '    0-15: "Source Port"\n'
            '    16-31: "Destination Port"'
        )
        assert isinstance(output, str)
        assert len(output) > 0

    def test_render_contains_field_labels(self):
        output = render(
            'packet-beta\n'
            '    0-15: "Source Port"\n'
            '    16-31: "Destination Port"\n'
            '    32-63: "Sequence Number"'
        )
        assert "Source Port" in output
        assert "Destination Port" in output
        assert "Sequence Number" in output

    def test_render_single_field(self):
        output = render(
            'packet-beta\n'
            '    0-31: "Header"'
        )
        assert "Header" in output

    def test_render_many_fields(self):
        output = render(
            'packet-beta\n'
            '    0-3: "Version"\n'
            '    4-7: "IHL"\n'
            '    8-15: "DSCP"\n'
            '    16-31: "Total Length"'
        )
        assert "Version" in output
        assert "IHL" in output
        assert "Total Length" in output
