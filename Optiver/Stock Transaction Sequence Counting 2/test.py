import unittest
from contextlib import redirect_stdout
from io import StringIO

from submission import countTransactionSequences


class DetailedTestResult(unittest.TextTestResult):
    """Show a concise pass count and the input responsible for a failure."""

    def _show_input(self, test):
        values = getattr(test, "current_input", "<input not recorded>")
        self.stream.writeln(f"Failing input (n, k, m): {values!r}")
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
    def run_count(self, n, k, m):
        self.current_input = (n, k, m)
        output = StringIO()
        try:
            with redirect_stdout(output):
                return countTransactionSequences(n, k, m)
        finally:
            self.debug_output = output.getvalue()

    def assert_count(self, n, k, m, expected):
        actual = self.run_count(n, k, m)
        self.assertIsInstance(actual, int)
        self.assertEqual(actual, expected)

    def test_given_example(self):
        self.assert_count(2, 1, 3, 4)

    def test_empty_sequence_when_already_at_target(self):
        self.assert_count(0, 0, 0, 1)

    def test_zero_transactions_away_from_target(self):
        self.assert_count(1, 0, 0, 0)

    def test_sell_can_reach_zero(self):
        self.assert_count(0, 1, 1, 1)

    def test_target_is_too_far_away(self):
        self.assert_count(10, 0, 9, 0)

    def test_at_most_m_includes_shorter_sequences(self):
        # Only buy,buy works. No sequence of length 1 or 3 can change the
        # position from 0 to 2 because of parity.
        self.assert_count(2, 0, 3, 1)

    def test_paths_below_zero_are_excluded(self):
        # Valid sequences are: sell; buy,sell,sell; sell,buy,sell.
        self.assert_count(0, 1, 3, 3)

    def test_multiple_returns_to_zero(self):
        # This sums all valid paths ending at zero for lengths 0 through 20.
        self.assert_count(0, 0, 20, 23714)

    def test_large_number_of_transactions(self):
        self.assert_count(0, 0, 50, 6619846420553)

    def test_extreme_large_result(self):
        self.assert_count(
            50,
            50,
            100,
            134979481538822650423771617309,
        )

    def test_extreme_target_requires_all_buys(self):
        self.assert_count(100, 0, 100, 1)


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
