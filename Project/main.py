from __future__ import annotations

import sys
from pathlib import Path

from codegen import CodeGenerator
from parser import CParser


def translate(input_path: str, output_path: str) -> None:
    source = Path(input_path).read_text(encoding="utf-8")
    parser = CParser()
    program = parser.parse(source)
    generator = CodeGenerator()
    output = generator.generate(program)
    Path(output_path).write_text(output, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("Usage: python main.py input.c output.py", file=sys.stderr)
        return 1
    input_path, output_path = argv
    translate(input_path, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
