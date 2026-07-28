import unittest
from contextlib import redirect_stdout
from io import StringIO

from submission import countTransactionSequences


def reference_count(n, order_sizes):
    """Independent iterative oracle used for large expected values."""
    dp = [0] * (n + 1)
    dp[0] = 1
    for total in range(1, n + 1):
        dp[total] = sum(
            dp[total - size] for size in order_sizes if size <= total
        )
    return dp[n]


class DetailedTestResult(unittest.TextTestResult):
    """Show a concise pass count and the input responsible for a failure."""

    def _show_input(self, test):
        values = getattr(test, "current_input", "<input not recorded>")
        self.stream.writeln(f"Failing input (n, k): {values!r}")
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
    def run_count(self, n, k):
        self.current_input = (n, k)
        output = StringIO()
        try:
            with redirect_stdout(output):
                return countTransactionSequences(n, k)
        finally:
            self.debug_output = output.getvalue()

    def assert_count(self, n, k, expected):
        actual = self.run_count(n, k)
        self.assertIsInstance(actual, int)
        self.assertEqual(actual, expected)

    def test_given_reachable_example(self):
        self.assert_count(3, [1, 2], 3)

    def test_given_unreachable_example(self):
        self.assert_count(3, [2, 4], 0)

    def test_zero_target_has_one_empty_sequence(self):
        self.assert_count(0, [1, 2], 1)

    def test_zero_target_with_large_order_sizes(self):
        self.assert_count(0, [100, 1000], 1)

    def test_target_one_reachable(self):
        self.assert_count(1, [1], 1)

    def test_target_one_unreachable(self):
        self.assert_count(1, [2, 3], 0)

    def test_order_sizes_larger_than_target_are_ignored(self):
        self.assert_count(4, [1, 2, 10, 100], 5)

    def test_all_order_sizes_larger_than_target(self):
        self.assert_count(7, [8, 9, 10], 0)

    def test_order_size_equal_to_target(self):
        self.assert_count(5, [5, 6, 20], 1)

    def test_single_order_size_divides_target(self):
        self.assert_count(12, [3], 1)

    def test_single_order_size_does_not_divide_target(self):
        self.assert_count(13, [3], 0)

    def test_order_matters(self):
        # [1,1,1,1], [1,3], and [3,1].
        self.assert_count(4, [1, 3], 3)

    def test_repeated_use_of_an_order_size(self):
        self.assert_count(6, [2, 3], 2)

    def test_permutations_of_the_same_sizes_are_distinct(self):
        # [2,2,3], [2,3,2], and [3,2,2].
        self.assert_count(7, [2, 3], 3)

    def test_three_consecutive_order_sizes(self):
        self.assert_count(6, [1, 2, 3], 24)

    def test_even_order_sizes_cannot_make_odd_target(self):
        self.assert_count(999, [2, 4, 10], 0)

    def test_common_divisor_can_make_large_target_unreachable(self):
        self.assert_count(1001, [6, 10, 14], 0)

    def test_unsorted_order_sizes(self):
        self.assert_count(5, [3, 1, 2], 13)

    def test_input_order_does_not_change_the_count(self):
        expected = 13
        for sizes in ([1, 2, 3], [3, 2, 1], [2, 3, 1]):
            with self.subTest(k=sizes):
                self.assert_count(5, list(sizes), expected)

    def test_many_permitted_order_sizes(self):
        sizes = list(range(1, 11))
        self.assert_count(100, sizes, reference_count(100, sizes))

    def test_large_fibonacci_like_result(self):
        self.assert_count(100, [1, 2], 573147844013817084101)

    def test_very_large_target_with_sparse_reachable_path(self):
        self.assert_count(10000, [1000], 1)

    def test_very_large_target_with_sparse_unreachable_path(self):
        self.assert_count(10001, [1000], 0)

    def test_zz_extreme_recursion_depth(self):
        # Easy for O(n) iterative DP, but deep recursive solutions may fail.
        self.assert_count(1000, [1, 2], reference_count(1000, [1, 2]))


if __name__ == "__main__":
    unittest.main(
        verbosity=2,
        testRunner=unittest.TextTestRunner(
            verbosity=2,
            resultclass=DetailedTestResult,
        ),
    )
