import sys

from parser import CParser
from transformer import ASTTransformer
from codegen import CodeGenerator
from semantic import SemanticAnalyzer, SemanticError


def translate(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        source = f.read()

    parser = CParser()
    tree = parser.parse(source)

    transformer = ASTTransformer()
    program = transformer.transform(tree)

    SemanticAnalyzer().analyze(program)

    generator = CodeGenerator()
    python_code = generator.generate(program)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(python_code)


def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <input.c> <output.py>")
        return 1

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    try:
        translate(input_path, output_path)

    except (SyntaxError, SemanticError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
