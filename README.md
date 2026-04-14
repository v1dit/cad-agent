# cad-agent

`cad-agent` is a minimal deterministic pipeline that turns natural language into a validated, engine-agnostic CAD specification before generating OpenSCAD output through an adapter layer.

This first version is intentionally small and structural. It models the core architecture:

```text
text -> parse -> validate -> adapter -> return scad
```

The parser is currently a placeholder and returns a hardcoded hollow-cylinder design tree. That keeps the current version deterministic while preserving the boundaries needed for future LLM parsing, correction loops, and backend execution.

## Why this project

Most AI CAD flows go straight from prompt to generated code. This project introduces a constraint-aware pipeline so geometry is structured, validated, and then translated into engine-specific output through adapters.

## Project Layout

```text
cad-agent/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── adapters/
│   │   │   ├── base.py
│   │   │   └── openscad.py
│   │   ├── generator.py
│   │   ├── parser.py
│   │   └── validator.py
│   ├── models/
│   │   └── schema.py
│   └── routes/
│       └── pipeline.py
├── examples/
│   └── test_prompt.txt
├── scripts/
│   └── run_pipeline.py
└── requirements.txt
```

## Quickstart

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the API:

```bash
python3 -m uvicorn app.main:app --reload
```

Run the CLI smoke test:

```bash
python3 scripts/run_pipeline.py
```

## API

Health check:

```bash
curl http://127.0.0.1:8000/
```

Pipeline request:

```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"text":"make a hollow cylinder"}'
```

Expected response shape:

```json
{
  "stage": "success",
  "engine": "openscad",
  "spec": {
    "type": "operation",
    "op": "difference",
    "children": [
      {
        "type": "primitive",
        "primitive": "cylinder",
        "parameters": {
          "radius": 5.0,
          "height": 10.0
        },
        "operation": "add"
      },
      {
        "type": "primitive",
        "primitive": "cylinder",
        "parameters": {
          "radius": 3.0,
          "height": 10.0
        },
        "operation": "add"
      }
    ]
  },
  "scad": "difference() {\n    cylinder(h=10.0, r=5.0);\n    cylinder(h=10.0, r=3.0);\n}"
}
```

## Abstract Spec

The current universal design spec supports two node types:

- `primitive` for engine-agnostic geometry primitives
- `operation` for boolean composition

The current placeholder prompt resolves to this shape:

```text
difference(
  cylinder(radius=5, height=10),
  cylinder(radius=3, height=10)
)
```

OpenSCAD is the only backend today, but it is now isolated behind an adapter instead of being baked into the pipeline contract.

## Current Limitations

- No LLM parser yet
- No correction loop
- No CAD engine execution
- No multi-agent orchestration
- Only cylinder primitives and `difference` are supported in the abstract spec

## Next Steps

- Replace the parser with structured LLM output
- Expand the abstract spec language
- Introduce a correction loop
- Add OpenSCAD execution and more backends
