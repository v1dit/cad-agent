import subprocess
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.adapters.openscad import OpenSCADAdapter
from app.core.parser import parse_prompt
from app.core.validator import validate_spec
from app.main import app
from app.models.schema import (
    CylinderParameters,
    OperationNode,
    PrimitiveNode,
    SphereParameters,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class IRExtensibilityTests(unittest.TestCase):
    maxDiff = None

    def test_parser_returns_hollow_cylinder_for_default_prompt(self) -> None:
        spec = parse_prompt("make a hollow cylinder")

        self.assertIsInstance(spec, OperationNode)
        self.assertEqual(spec.op, "difference")
        self.assertEqual(len(spec.children), 2)

    def test_parser_returns_sphere_for_sphere_prompt(self) -> None:
        spec = parse_prompt("make a sphere")

        self.assertIsInstance(spec, PrimitiveNode)
        self.assertEqual(spec.primitive, "sphere")
        self.assertIsInstance(spec.parameters, SphereParameters)
        self.assertEqual(spec.parameters.radius, 4)

    def test_parser_returns_nested_union_demo(self) -> None:
        spec = parse_prompt("make a union of a hollow cylinder and a sphere")

        self.assertIsInstance(spec, OperationNode)
        self.assertEqual(spec.op, "union")
        self.assertEqual(len(spec.children), 2)
        self.assertIsInstance(spec.children[0], OperationNode)
        self.assertIsInstance(spec.children[1], PrimitiveNode)

    def test_validator_accepts_valid_sphere(self) -> None:
        spec = PrimitiveNode(
            type="primitive",
            primitive="sphere",
            parameters=SphereParameters(radius=2),
        )

        validation = validate_spec(spec)
        self.assertTrue(validation.valid)
        self.assertEqual(validation.errors, [])

    def test_validator_rejects_invalid_sphere(self) -> None:
        spec = PrimitiveNode(
            type="primitive",
            primitive="sphere",
            parameters=SphereParameters(radius=0),
        )

        validation = validate_spec(spec)
        self.assertFalse(validation.valid)
        self.assertIn("sphere radius must be positive", validation.errors)

    def test_validator_accepts_valid_union(self) -> None:
        spec = OperationNode(
            type="operation",
            op="union",
            children=[
                PrimitiveNode(
                    type="primitive",
                    primitive="cylinder",
                    parameters=CylinderParameters(radius=5, height=10),
                ),
                PrimitiveNode(
                    type="primitive",
                    primitive="sphere",
                    parameters=SphereParameters(radius=3),
                ),
            ],
        )

        validation = validate_spec(spec)
        self.assertTrue(validation.valid)
        self.assertEqual(validation.errors, [])

    def test_validator_rejects_union_with_too_few_children(self) -> None:
        spec = OperationNode(
            type="operation",
            op="union",
            children=[
                PrimitiveNode(
                    type="primitive",
                    primitive="sphere",
                    parameters=SphereParameters(radius=3),
                )
            ],
        )

        validation = validate_spec(spec)
        self.assertFalse(validation.valid)
        self.assertIn("union operations must have at least two children", validation.errors)

    def test_validator_accepts_nested_union_with_difference_subtree(self) -> None:
        spec = parse_prompt("make a union of a hollow cylinder and a sphere")

        validation = validate_spec(spec)
        self.assertTrue(validation.valid)
        self.assertEqual(validation.errors, [])

    def test_adapter_renders_sphere(self) -> None:
        spec = PrimitiveNode(
            type="primitive",
            primitive="sphere",
            parameters=SphereParameters(radius=4),
        )

        output = OpenSCADAdapter().generate(spec)
        self.assertEqual(output, "sphere(r=4.0);")

    def test_adapter_renders_union(self) -> None:
        spec = OperationNode(
            type="operation",
            op="union",
            children=[
                PrimitiveNode(
                    type="primitive",
                    primitive="cylinder",
                    parameters=CylinderParameters(radius=5, height=10),
                ),
                PrimitiveNode(
                    type="primitive",
                    primitive="sphere",
                    parameters=SphereParameters(radius=4),
                ),
            ],
        )

        output = OpenSCADAdapter().generate(spec)
        self.assertEqual(
            output,
            "union() {\n"
            "    cylinder(h=10.0, r=5.0);\n"
            "    sphere(r=4.0);\n"
            "}",
        )

    def test_adapter_renders_nested_mixed_tree(self) -> None:
        output = OpenSCADAdapter().generate(parse_prompt("make a union of a hollow cylinder and a sphere"))
        self.assertEqual(
            output,
            "union() {\n"
            "    difference() {\n"
            "        cylinder(h=10.0, r=5.0);\n"
            "        cylinder(h=10.0, r=3.0);\n"
            "    }\n"
            "    sphere(r=4.0);\n"
            "}",
        )

    def test_api_returns_sphere_demo(self) -> None:
        client = TestClient(app)
        response = client.post("/run", json={"text": "make a sphere"})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["engine"], "openscad")
        self.assertEqual(body["spec"]["primitive"], "sphere")
        self.assertEqual(body["scad"], "sphere(r=4.0);")

    def test_api_returns_union_demo(self) -> None:
        client = TestClient(app)
        response = client.post("/run", json={"text": "make a union of a hollow cylinder and a sphere"})

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["engine"], "openscad")
        self.assertEqual(body["spec"]["op"], "union")
        self.assertIn("difference()", body["scad"])
        self.assertIn("sphere(r=4.0);", body["scad"])

    def test_cli_runs_sphere_prompt_file(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/run_pipeline.py", "examples/sphere_prompt.txt"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.strip(), "sphere(r=4.0);")

    def test_cli_runs_union_prompt_file(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/run_pipeline.py", "examples/union_prompt.txt"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("union() {", result.stdout)
        self.assertIn("difference() {", result.stdout)
        self.assertIn("sphere(r=4.0);", result.stdout)


if __name__ == "__main__":
    unittest.main()
