# cad-agent

`cad-agent` is a minimal deterministic pipeline that turns natural language into a validated CAD specification before generating OpenSCAD output.

This first version is intentionally small and structural. It models the core architecture:

```text
text -> parse -> validate -> generate -> return scad
```

The parser is currently a placeholder and returns a hardcoded hollow-cylinder spec. That keeps the first commit deterministic while preserving the boundaries needed for future LLM parsing, correction loops, and backend execution.

## Why this project

Most AI CAD flows go straight from prompt to generated code. This project introduces a constraint-aware pipeline so geometry is structured and validated before execution.

## Project Layout

```text
cad-agent/
├── app/
│   ├── main.py
│   ├── core/
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
uvicorn app.main:app --reload
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
  "spec": {
    "shape": "cylinder",
    "outer_radius": 5.0,
    "inner_radius": 3.0,
    "height": 10.0
  },
  "scad": "difference() {\n    cylinder(h=10.0, r=5.0);\n    cylinder(h=10.0, r=3.0);\n}"
}
```

## Current Limitations

- No LLM parser yet
- No correction loop
- No CAD engine execution
- No multi-agent orchestration

## Next Steps

- Replace the parser with structured LLM output
- Add stricter schema enforcement
- Introduce a correction loop
- Add OpenSCAD execution and more backends
