#!/usr/bin/env python3
"""
Regenerate the OpenAPI specification from the running FastAPI app definition.

Usage:
    uv run python scripts/generate_openapi.py

This writes docs/api/openapi.json which is used for:
- Interactive docs (/docs and /redoc when the server is running)
- Static reference documentation
- Potential client code generation
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running from project root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nutriplan.api.main import app


def main() -> None:
    output_path = Path("docs/api/openapi.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    openapi_schema = app.openapi()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"✅ OpenAPI specification written to {output_path}")
    print(f"   Title: {openapi_schema['info']['title']}")
    print(f"   Version: {openapi_schema['info']['version']}")
    print(f"   Paths: {len(openapi_schema.get('paths', {}))}")


if __name__ == "__main__":
    main()