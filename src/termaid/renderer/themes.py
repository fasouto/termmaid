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
    "blueprint": Theme(
        name="blueprint",
        node="#90CAF9",
        edge="#5C6BC0",
        arrow="bold #E3F2FD",
        subgraph="#7986CB",
        label="bold #FFFFFF",
        edge_label="italic #B3E5FC",
        subgraph_label="bold #E8EAF6",
        is_solid=True,
        bg_default="on #1A237E",
        bg_node="on #283593",
        bg_subgraph="on #1E2A78",
    ),
    "slate": Theme(
        name="slate",
        node="#CFD8DC",
        edge="#78909C",
        arrow="bold #FF8A65",
        subgraph="#90A4AE",
        label="bold #ECEFF1",
        edge_label="italic #B0BEC5",
        subgraph_label="bold #B0BEC5",
        is_solid=True,
        bg_default="on #263238",
        bg_node="on #37474F",
        bg_subgraph="on #2E3B42",
    ),
    "sunset": Theme(
        name="sunset",
        node="#F48FB1",
        edge="#CE93D8",
        arrow="bold #FFD54F",
        subgraph="#F06292",
        label="bold #FCE4EC",
        edge_label="italic #F8BBD0",
        subgraph_label="bold #F8BBD0",
        is_solid=True,
        bg_default="on #880E4F",
        bg_node="on #AD1457",
        bg_subgraph="on #9C1458",
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
}


def get_theme(name: str) -> Theme:
    """Get a theme by name, falling back to default."""
    return THEMES.get(name, THEMES["default"])
