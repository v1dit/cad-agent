# cad-agent

`cad-agent` is a deterministic geometry compiler skeleton that turns natural language into a validated, engine-agnostic CAD specification before generating and optionally executing OpenSCAD through an adapter layer.

This first version is intentionally small and structural. It models the core architecture:

```text
text -> parse -> normalize -> validate -> adapter -> code -> optional execution
```

The parser is currently a placeholder and maps a few fixed prompt patterns into deterministic design trees. That keeps the current version predictable while preserving the boundaries needed for future LLM parsing, correction loops, and backend execution.

## Why this project

Most AI CAD flows go straight from prompt to generated code. This project introduces a constraint-aware pipeline so geometry is structured, validated, and then translated into engine-specific output through adapters.

## IR Contract

The IR language for this project is documented in [docs/IR_SPEC.md](docs/IR_SPEC.md). That document defines:

- supported node kinds
- primitives and operations
- units and coordinate conventions
- normalization rules
- structural and semantic invariants

## Project Layout

```text
cad-agent/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── adapters/
│   │   │   ├── base.py
│   │   │   ├── registry.py
│   │   │   └── openscad.py
│   │   ├── executor.py
│   │   ├── generator.py
│   │   ├── normalize.py
│   │   ├── parser.py
│   │   └── validator.py
│   ├── models/
│   │   └── schema.py
│   └── routes/
│       └── pipeline.py
├── docs/
│   └── IR_SPEC.md
├── examples/
│   ├── cube_prompt.txt
│   ├── intersection_prompt.txt
│   ├── sphere_prompt.txt
│   ├── test_prompt.txt
│   └── union_prompt.txt
├── scripts/
│   └── run_pipeline.py
├── tests/
│   └── test_ir_extensibility.py
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

Run alternate deterministic demos:

```bash
python3 scripts/run_pipeline.py examples/cube_prompt.txt
python3 scripts/run_pipeline.py examples/intersection_prompt.txt
python3 scripts/run_pipeline.py examples/sphere_prompt.txt
python3 scripts/run_pipeline.py examples/union_prompt.txt
```

Generate code and attempt execution:

```bash
python3 scripts/run_pipeline.py --execute examples/sphere_prompt.txt
```

Run the test suite:

```bash
python3 -m unittest discover -s tests
```

Execution requires the `openscad` CLI to be installed and available on `PATH`.

## API

Health check:

```bash
curl http://127.0.0.1:8000/
```

Pipeline request for a hollow cylinder:

```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"text":"make a hollow cylinder"}'
```

Pipeline request that also attempts execution:

```bash
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"text":"make a sphere","execute":true}'
```

Expected success response shape:

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
  "output": {
    "type": "scad",
    "code": "difference() {\n    cylinder(h=10.0, r=5.0);\n    cylinder(h=10.0, r=3.0);\n}"
  },
  "artifact": null
}
```

Expected execution failure shape when `openscad` is unavailable:

```json
{
  "stage": "execution_failed",
  "engine": "openscad",
  "errors": [
    "openscad executable not found in PATH"
  ],
  "spec": {
    "type": "primitive",
    "primitive": "sphere",
    "parameters": {
      "radius": 4.0
    },
    "operation": "add"
  },
  "output": {
    "type": "scad",
    "code": "sphere(r=4.0);"
  }
}
```

## Abstract Spec

The current universal design spec supports two node types:

- `primitive` for engine-agnostic geometry primitives
- `operation` for boolean composition

The current milestone supports:

- primitives: `cylinder`, `sphere`, `cube`
- operations: `difference`, `union`, `intersection`

Every request follows the same compiler stages:

- parse a deterministic demo tree
- normalize the IR
- validate structural and semantic invariants
- generate backend code
- optionally execute through the adapter

The placeholder parser currently recognizes a few deterministic demos:

- prompts containing `sphere` -> sphere primitive
- prompts containing `cube` -> cube primitive
- prompts containing `union` -> nested union demo
- prompts containing `intersection` -> cube/sphere intersection demo
- all other prompts -> hollow cylinder difference tree

The default prompt resolves to this shape:

```text
difference(
  cylinder(radius=5, height=10),
  cylinder(radius=3, height=10)
)
```

A union demo resolves to:

```text
union(
  difference(
    cylinder(radius=5, height=10),
    cylinder(radius=3, height=10)
  ),
  sphere(radius=4)
)
```

An intersection demo resolves to:

```text
intersection(
  cube(width=6, depth=6, height=6),
  sphere(radius=4)
)
```

OpenSCAD is the only backend today, but it is now isolated behind an adapter instead of being baked into the pipeline contract.

## Current Limitations

- No LLM parser yet
- No correction loop
- Only one backend adapter is implemented
- No multi-agent orchestration
- No transforms, assemblies, or engine selection yet

## Next Steps

- Replace the parser with structured LLM output
- Add more primitives and boolean operations carefully
- Add more execution-capable backends
- Introduce a correction loop
- Expand normalization and semantic constraints
