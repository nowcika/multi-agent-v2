import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal

HERE = Path(__file__).resolve().parent

class TotalsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.csv = Path(self.tmp.name) / 'input.csv'

    def run_cli(self, contents):
        self.csv.write_text(contents, encoding='utf-8')
        return subprocess.run([sys.executable, str(HERE / 'totals.py'), str(self.csv)], text=True, capture_output=True)

    def assert_total(self, contents, expected):
        result = self.run_cli(contents)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        self.assertEqual(json.loads(result.stdout), {'total': expected})

    def test_normal(self):
        self.assert_total('amount,note\n12.50,a\n-2.25,b\n', '10.25')

    def test_blank_values(self):
        self.assert_total('amount,note\n,a\n   ,b\n 2.50 ,c\n', '2.50')

    def test_decimal_exact(self):
        self.assert_total('amount\n0.1\n0.2\n', '0.3')

    def test_long_decimal_exact(self):
        self.assert_total('amount\n123456789012345678901234567890.1\n0.2\n', '123456789012345678901234567890.3')

    def test_header_only(self):
        self.assert_total('amount\n', '0')

    def test_invalid_value_reports_line(self):
        result = self.run_cli('amount\n1\nwrong\n')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertIn('3', result.stderr)
        self.assertIn('wrong', result.stderr)

    def test_nonfinite_invalid(self):
        for token in ['NaN', 'Infinity', '-Infinity']:
            with self.subTest(token=token):
                result = self.run_cli('amount\n' + token + '\n')
                self.assertEqual(result.returncode, 2)
                self.assertIn('2', result.stderr)

    def test_missing_header_and_empty_file(self):
        for contents in ['', 'price\n2\n']:
            with self.subTest(contents=contents):
                result = self.run_cli(contents)
                self.assertEqual(result.returncode, 2)
                self.assertTrue(result.stderr)

    def test_api_and_main(self):
        spec = importlib.util.spec_from_file_location('totals_under_test', HERE / 'totals.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.csv.write_text('amount\n0.1\n0.2\n', encoding='utf-8')
        total = module.sum_amounts(self.csv)
        self.assertIsInstance(total, Decimal)
        self.assertEqual(total, Decimal('0.3'))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = module.main([str(self.csv)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue()), {'total': '0.3'})

if __name__ == '__main__':
    unittest.main()
