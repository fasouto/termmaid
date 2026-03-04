"""CLI entry point for termmaid."""
from __future__ import annotations

import argparse
import os
import sys


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="termmaid",
        description="Render Mermaid diagrams as Unicode art in the terminal",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Mermaid diagram file (.mmd). Reads from stdin if not provided.",
    )
    parser.add_argument(
        "--ascii",
        action="store_true",
        help="Use ASCII characters instead of Unicode box-drawing",
    )
    parser.add_argument(
        "--padding-x",
        type=int,
        default=4,
        help="Horizontal padding inside node boxes (default: 4)",
    )
    parser.add_argument(
        "--padding-y",
        type=int,
        default=2,
        help="Vertical padding inside node boxes (default: 2)",
    )
    parser.add_argument(
        "--sharp-edges",
        action="store_true",
        help="Use sharp corners on edge turns (┌┐└┘) instead of rounded (╭╮╰╯)",
    )
    parser.add_argument(
        "--theme",
        default=None,
        choices=["default", "terra", "neon", "mono", "amber", "phosphor"],
        help="Color theme. Requires 'rich' package (pip install termmaid[rich]).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    args = parser.parse_args(argv)

    use_color = args.theme is not None
    theme = args.theme or "default"

    # Read input
    if args.file:
        try:
            with open(args.file) as f:
                source = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 1
        except OSError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 1
    elif not sys.stdin.isatty():
        source = sys.stdin.read()
    else:
        print("Error: No input provided. Pass a file or pipe input.", file=sys.stderr)
        print("Usage: termmaid diagram.mmd", file=sys.stderr)
        print("       echo 'graph LR; A-->B' | termmaid", file=sys.stderr)
        return 1

    source = source.strip()
    if not source:
        print("Error: Empty input.", file=sys.stderr)
        return 1

    try:
        from termmaid import render, render_rich
    except ImportError:
        # Support running directly: python3 src/termmaid/cli.py
        # __file__ is src/termmaid/cli.py → go up to src/
        _src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, _src_dir)
        try:
            from termmaid import render, render_rich
        except ImportError:
            print("Error: termmaid package not found. Install with: pip install -e .", file=sys.stderr)
            return 1

    try:
        if use_color:
            result = render_rich(
                source,
                use_ascii=args.ascii,
                padding_x=args.padding_x,
                padding_y=args.padding_y,
                rounded_edges=not args.sharp_edges,
                theme=theme,
            )
            try:
                from rich import print as rprint
                rprint(result)
            except ImportError:
                print("Error: 'rich' package required for --theme. Install with: pip install termmaid[rich]", file=sys.stderr)
                return 1
        else:
            result = render(
                source,
                use_ascii=args.ascii,
                padding_x=args.padding_x,
                padding_y=args.padding_y,
                rounded_edges=not args.sharp_edges,
            )
            print(result)
    except Exception as e:
        print(f"Error rendering diagram: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
