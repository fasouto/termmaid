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
}


def get_theme(name: str) -> Theme:
    """Get a theme by name, falling back to default."""
    return THEMES.get(name, THEMES["default"])
