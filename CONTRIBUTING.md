# Contributing to termmaid

## Development setup

```bash
git clone https://github.com/fasouto/termmaid.git
cd termmaid
uv sync --all-extras
```

## Running tests

```bash
uv run pytest tests/ -q
```

To update snapshot tests after changing rendering output:

```bash
uv run pytest tests/ --update-snapshots
```

## Project structure

```
src/termmaid/
  __init__.py          # Public API: parse(), render(), render_rich()
  cli.py               # CLI entry point
  graph/               # Data models (Graph, Node, Edge, NodeShape)
  parser/              # Mermaid syntax parsing (flowchart, statediagram)
  layout/              # Grid-based layout computation
  routing/             # A* edge routing
  renderer/            # Canvas rendering, shapes, charsets
  output/              # Output formats (text, rich, textual widget)
tests/
  fixtures/flowcharts/ # .mmd input fixtures + expected .txt outputs
```

## Adding a new node shape

1. Add the shape to `NodeShape` enum in `src/termmaid/graph/shapes.py`
2. Add parser detection in `src/termmaid/parser/flowchart.py` (`_parse_node`)
3. Add renderer in `src/termmaid/renderer/shapes/__init__.py`
4. Register in `SHAPE_RENDERERS` dict
5. Add tests in `tests/test_shapes.py`

## Adding a test fixture

1. Create `tests/fixtures/flowcharts/my_test.mmd`
2. Run `uv run pytest tests/test_renderer.py -q` — it auto-generates the expected output
3. Review the generated `.txt` file in `tests/fixtures/expected/`
4. Run again to confirm it passes
