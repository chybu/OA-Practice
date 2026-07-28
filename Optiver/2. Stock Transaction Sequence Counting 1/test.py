import unittest
from contextlib import redirect_stdout
from io import StringIO

from submission import countTransactionSequences


class DetailedTestResult(unittest.TextTestResult):
    """Show a concise pass count and the input responsible for a failure."""

    def _show_input(self, test):
        n = getattr(test, "current_input", "<input not recorded>")
        self.stream.writeln(f"Failing input: n = {n!r}")
        debug_output = getattr(test, "debug_output", "").strip()
        if debug_output:
            self.stream.writeln(f"Captured debug output:\n{debug_output}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._show_input(test)

    def addError(self, test, err):
        super().addError(test, err)
        self._show_input(test)

    def stopTestRun(self):
        super().stopTestRun()
        skipped = len(self.skipped)
        passed = self.testsRun - len(self.failures) - len(self.errors) - skipped
        self.stream.writeln(
            f"Passed: {passed}/{self.testsRun} "
            f"(failed: {len(self.failures)}, errors: {len(self.errors)}, "
            f"skipped: {skipped})"
        )


class CountTransactionSequencesTests(unittest.TestCase):
    def run_count(self, n):
        self.current_input = n
        output = StringIO()
        try:
            with redirect_stdout(output):
                return countTransactionSequences(n)
        finally:
            self.debug_output = output.getvalue()

    def assert_count(self, n, expected):
        actual = self.run_count(n)
        self.assertIsInstance(actual, int)
        self.assertEqual(actual, expected)

    def test_zero_transactions_has_one_empty_sequence(self):
        self.assert_count(0, 1)

    def test_single_buy_and_sell(self):
        self.assert_count(1, 1)

    def test_given_example(self):
        self.assert_count(2, 2)

    def test_three_pairs(self):
        self.assert_count(3, 5)

    def test_small_catalan_numbers(self):
        expected = {
            4: 14,
            5: 42,
            6: 132,
            7: 429,
            8: 1430,
            9: 4862,
            10: 16796,
        }
        for n, count in expected.items():
            with self.subTest(n=n):
                self.assert_count(n, count)

    def test_moderately_large_input(self):
        self.assert_count(12, 208012)

    def test_maximum_constraint(self):
        self.assert_count(35, 3116285494907301262)


if __name__ == "__main__":
    unittest.main(
        verbosity=2,
        failfast=True,
        testRunner=unittest.TextTestRunner(
            verbosity=2,
            failfast=True,
            resultclass=DetailedTestResult,
        ),
    )
