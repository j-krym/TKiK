from __future__ import annotations

import contextlib
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codegen import CodeGenerator
from parser import CParser


def translate(source: str) -> str:
    parser = CParser()
    program = parser.parse(source)
    return CodeGenerator().generate(program)


class TranslatorTests(unittest.TestCase):
    def test_assignment(self):
        source = """
        int main() {
            int x = 5;
            x = x + 2;
            return x;
        }
        """
        py = translate(source)
        self.assertIn("x = 5", py)
        self.assertIn("x = x + 2", py)
        ns: dict[str, object] = {}
        exec(py, ns)
        self.assertEqual(ns["main"](), 7)

    def test_loop(self):
        source = """
        int main() {
            int i = 0;
            int total = 0;
            for (i = 0; i < 5; i = i + 1) {
                total = total + i;
            }
            return total;
        }
        """
        py = translate(source)
        self.assertIn("while i < 5:", py)
        ns: dict[str, object] = {}
        exec(py, ns)
        self.assertEqual(ns["main"](), 10)

    def test_function(self):
        source = """
        int add(int a, int b) {
            return a + b;
        }

        int main() {
            return add(2, 3);
        }
        """
        py = translate(source)
        self.assertIn("def add(a, b):", py)
        ns: dict[str, object] = {}
        exec(py, ns)
        self.assertEqual(ns["main"](), 5)

    def test_printf(self):
        source = """
        int main() {
            int result = 5;
            printf("%d\n", result);
            return 0;
        }
        """
        py = translate(source)
        self.assertIn('print("%d\n" % result, end="")', py)
        ns: dict[str, object] = {}
        exec(py, ns)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ns["main"]()
        self.assertEqual(buf.getvalue(), "5\n")

    def test_ternary(self):
        source = """
        int main() {
            int a = 4;
            int b = a > 3 ? 1 : 2;
            return b;
        }
        """
        py = translate(source)
        self.assertIn("if a > 3 else", py)
        ns: dict[str, object] = {}
        exec(py, ns)
        self.assertEqual(ns["main"](), 1)

    def test_switch(self):
        source = """
        int main() {
            int x = 2;
            int result = 0;
            switch (x) {
                case 1:
                    result = 10;
                    break;
                case 2:
                    result = 20;
                    break;
                default:
                    result = 30;
                    break;
            }
            return result;
        }
        """
        py = translate(source)
        self.assertIn("if __switch_value == 1:", py)
        self.assertIn("elif __switch_value == 2:", py)
        ns: dict[str, object] = {}
        exec(py, ns)
        self.assertEqual(ns["main"](), 20)


if __name__ == "__main__":
    unittest.main()
