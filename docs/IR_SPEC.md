# IR Specification v1

`cad-agent` uses a tree-shaped intermediate representation (IR) to describe geometry independently of any specific CAD backend.

## Goals

- Represent geometry as a deterministic, backend-agnostic language
- Keep adapter-specific syntax out of the IR
- Support recursive validation, normalization, generation, and execution

## Units and Coordinates

- All dimensions are expressed in millimeters
- The coordinate system is right-handed
- Primitive-local axes follow these conventions:
  - `cylinder`: centered on the XY plane and extends along positive Z from `z=0` to `z=height`
  - `sphere`: centered at the origin
  - `cube`: anchored at the origin and extends along positive X, Y, and Z

## Node Kinds

Every node is exactly one of:

- `primitive`
- `operation`

No node may mix `primitive` and `op` fields.

## Primitive Nodes

Primitive nodes describe solid geometry and must include:

- `type`
- `primitive`
- `parameters`
- `operation`

### Common Invariants

- `type` must be `"primitive"`
- `operation` must be `"add"`
- No adapter-specific fields are allowed

### Supported Primitives

#### Cylinder

```json
{
  "type": "primitive",
  "primitive": "cylinder",
  "parameters": {
    "radius": 5.0,
    "height": 10.0
  },
  "operation": "add"
}
```

Rules:

- `radius > 0`
- `height > 0`

#### Sphere

```json
{
  "type": "primitive",
  "primitive": "sphere",
  "parameters": {
    "radius": 4.0
  },
  "operation": "add"
}
```

Rules:

- `radius > 0`

#### Cube

```json
{
  "type": "primitive",
  "primitive": "cube",
  "parameters": {
    "width": 6.0,
    "depth": 6.0,
    "height": 6.0
  },
  "operation": "add"
}
```

Rules:

- `width > 0`
- `depth > 0`
- `height > 0`

## Operation Nodes

Operation nodes compose child geometry and must include:

- `type`
- `op`
- `children`

### Common Invariants

- `type` must be `"operation"`
- `children` must contain only valid IR nodes
- No adapter-specific fields are allowed

### Supported Operations

#### Union

```json
{
  "type": "operation",
  "op": "union",
  "children": [ ... ]
}
```

Rules:

- At least 2 children
- Nested unions may be flattened during normalization

#### Difference

```json
{
  "type": "operation",
  "op": "difference",
  "children": [ ... ]
}
```

Rules:

- At least 2 children
- The first child is the base solid
- Remaining children are subtractive solids
- For the current hollow-cylinder demo shape, subtractive cylinder radii must be smaller than the base cylinder radius

#### Intersection

```json
{
  "type": "operation",
  "op": "intersection",
  "children": [ ... ]
}
```

Rules:

- At least 2 children
- Nested intersections may be flattened during normalization

## Normalization Rules

Before validation and generation, IR trees are normalized using these rules:

- Nested `union` nodes are flattened
- Nested `intersection` nodes are flattened
- `difference` retains its first child as the base solid
- Zero-sized primitives may be removed from `union` and `intersection` children as no-ops
- A normalized tree is idempotent: normalizing twice yields the same tree

## Example Trees

### Hollow Cylinder

```text
difference(
  cylinder(radius=5, height=10),
  cylinder(radius=3, height=10)
)
```

### Union Demo

```text
union(
  difference(
    cylinder(radius=5, height=10),
    cylinder(radius=3, height=10)
  ),
  sphere(radius=4)
)
```

### Intersection Demo

```text
intersection(
  cube(width=6, depth=6, height=6),
  sphere(radius=4)
)
```
