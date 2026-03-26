"""Theme system for colored diagram output."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """Maps semantic style keys to Rich style strings."""
    name: str
    node: str
    edge: str
    arrow: str
    subgraph: str
    label: str
    edge_label: str
    subgraph_label: str
    default: str = ""
    # Solid-background themes fill regions with bg colors
    is_solid: bool = False
    bg_default: str = ""     # overall background
    bg_node: str = ""        # node box fill
    bg_subgraph: str = ""    # subgraph region fill


THEMES: dict[str, Theme] = {
    "default": Theme(
        name="default",
        node="cyan",
        edge="dim white",
        arrow="bold yellow",
        subgraph="dim cyan",
        label="bold white",
        edge_label="italic dim",
        subgraph_label="bold cyan",
    ),
    "terra": Theme(
        name="terra",
        node="bold #D4845A",
        edge="#8B7E6A",
        arrow="bold #E8A87C",
        subgraph="#A07858",
        label="#F5E6D3",
        edge_label="italic #B89A7A",
        subgraph_label="bold #E8A87C",
    ),
    "neon": Theme(
        name="neon",
        node="bold magenta",
        edge="dim cyan",
        arrow="bold green",
        subgraph="dim magenta",
        label="bold white",
        edge_label="italic cyan",
        subgraph_label="bold cyan",
    ),
    "mono": Theme(
        name="mono",
        node="bold white",
        edge="dim",
        arrow="bold white",
        subgraph="dim",
        label="white",
        edge_label="italic dim",
        subgraph_label="bold white",
    ),
    "amber": Theme(
        name="amber",
        node="bold #FFB000",
        edge="#806000",
        arrow="bold #FFD080",
        subgraph="#906800",
        label="#FFD580",
        edge_label="italic #B08030",
        subgraph_label="bold #FFC040",
    ),
    "phosphor": Theme(
        name="phosphor",
        node="bold #33FF33",
        edge="#1A8C1A",
        arrow="bold #66FF66",
        subgraph="#228B22",
        label="#AAFFAA",
        edge_label="italic #339933",
        subgraph_label="bold #55DD55",
    ),
    "gruvbox": Theme(
        name="gruvbox",
        node="#FABD2F",
        edge="#8EC07C",
        arrow="bold #FE8019",
        subgraph="#B8BB26",
        label="bold #EBDBB2",
        edge_label="italic #D5C4A1",
        subgraph_label="bold #D5C4A1",
        is_solid=True,
        bg_default="on #282828",
        bg_node="on #3C3836",
        bg_subgraph="on #32302F",
    ),
    "monokai": Theme(
        name="monokai",
        node="#F92672",
        edge="#66D9EF",
        arrow="bold #A6E22E",
        subgraph="#AE81FF",
        label="bold #F8F8F2",
        edge_label="italic #E6DB74",
        subgraph_label="bold #AE81FF",
        is_solid=True,
        bg_default="on #272822",
        bg_node="on #3E3D32",
        bg_subgraph="on #333328",
    ),
    "dracula": Theme(
        name="dracula",
        node="#BD93F9",
        edge="#6272A4",
        arrow="bold #50FA7B",
        subgraph="#FF79C6",
        label="bold #F8F8F2",
        edge_label="italic #8BE9FD",
        subgraph_label="bold #FF79C6",
        is_solid=True,
        bg_default="on #282A36",
        bg_node="on #44475A",
        bg_subgraph="on #383A4A",
    ),
    "nord": Theme(
        name="nord",
        node="#88C0D0",
        edge="#4C566A",
        arrow="bold #A3BE8C",
        subgraph="#81A1C1",
        label="bold #ECEFF4",
        edge_label="italic #B48EAD",
        subgraph_label="bold #81A1C1",
        is_solid=True,
        bg_default="on #2E3440",
        bg_node="on #3B4252",
        bg_subgraph="on #343C4A",
    ),
    "solarized": Theme(
        name="solarized",
        node="#268BD2",
        edge="#586E75",
        arrow="bold #B58900",
        subgraph="#2AA198",
        label="bold #FDF6E3",
        edge_label="italic #CB4B16",
        subgraph_label="bold #2AA198",
        is_solid=True,
        bg_default="on #002B36",
        bg_node="on #073642",
        bg_subgraph="on #053440",
    ),
}


def get_theme(name: str) -> Theme:
    """Get a theme by name, falling back to default."""
    return THEMES.get(name, THEMES["default"])
