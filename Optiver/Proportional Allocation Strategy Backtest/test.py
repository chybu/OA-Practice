import math
import unittest
from contextlib import redirect_stdout
from io import StringIO

from submission import BacktestStatistics


class DetailedTestResult(unittest.TextTestResult):
    """Show a concise pass count and the input responsible for a failure."""

    def _show_input(self, test):
        timeseries = getattr(test, "current_input", "<input not recorded>")
        self.stream.writeln(f"Failing input: {timeseries!r}")
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


class BacktestStatisticsTests(unittest.TestCase):
    def runBacktest(self, timeseries):
        self.current_input = timeseries
        output = StringIO()
        try:
            with redirect_stdout(output):
                return BacktestStatistics(timeseries)
        finally:
            self.debug_output = output.getvalue()

    def assertStatisticsAlmostEqual(self, actual, expected):
        self.assertIsInstance(actual, (list, tuple))
        self.assertEqual(len(actual), 2)
        for position, (actual_value, expected_value) in enumerate(
            zip(actual, expected)
        ):
            self.assertTrue(
                math.isclose(actual_value, expected_value, rel_tol=1e-9, abs_tol=1e-9),
                msg=(
                    f"Result at index {position} differs: "
                    f"expected {expected_value}, got {actual_value}"
                ),
            )

    def test_worked_example(self):
        timeseries = [
            [100.0, 115.0, 117.3],
            [200.0, 210.0, 199.5],
        ]
        daily_log_return = math.log(1.0025)
        expected = [daily_log_return / 2, daily_log_return / 2]
        self.assertStatisticsAlmostEqual(self.runBacktest(timeseries), expected)

    def test_all_non_positive_returns_means_hold_cash(self):
        timeseries = [
            [100.0, 90.0, 80.0, 80.0],
            [200.0, 200.0, 190.0, 180.0],
        ]
        self.assertStatisticsAlmostEqual(
            self.runBacktest(timeseries), [0.0, 0.0]
        )

    def test_positive_returns_are_used_as_proportional_weights(self):
        timeseries = [
            [100.0, 110.0, 121.0],
            [100.0, 120.0, 108.0],
        ]
        # Day 1 weights are 1/3 and 2/3. The next simple portfolio
        # return is (1/3 * 10%) + (2/3 * -10%) = -1/30.
        second_period_log_return = math.log(29 / 30)
        expected = [
            second_period_log_return / 2,
            abs(second_period_log_return) / 2,
        ]
        self.assertStatisticsAlmostEqual(self.runBacktest(timeseries), expected)

    def test_single_stock_can_be_sold_after_a_negative_return(self):
        timeseries = [[100.0, 110.0, 121.0, 108.9, 217.8]]
        # Period returns are 0%, +10%, -10%, then 0% because the stock
        # was sold after its negative return and the portfolio holds cash.
        returns = [0.0, math.log(1.1), math.log(0.9), 0.0]
        mean = sum(returns) / len(returns)
        variance = sum((value - mean) ** 2 for value in returns) / len(returns)
        self.assertStatisticsAlmostEqual(
            self.runBacktest(timeseries), [mean, math.sqrt(variance)]
        )

    def test_two_days_always_has_zero_return(self):
        timeseries = [
            [100.0, 150.0],
            [200.0, 100.0],
        ]
        # There is only the initial period, when the fund must remain in cash.
        self.assertStatisticsAlmostEqual(
            self.runBacktest(timeseries), [0.0, 0.0]
        )

    def test_unchanged_stock_is_excluded_from_allocation(self):
        timeseries = [
            [100.0, 110.0, 121.0],
            [100.0, 100.0, 200.0],
        ]
        # Only stock 0 rose on day 1, so it receives the entire allocation.
        # Stock 1's later 100% gain must not affect the portfolio return.
        returns = [0.0, math.log(1.1)]
        mean = sum(returns) / len(returns)
        variance = sum((value - mean) ** 2 for value in returns) / len(returns)
        self.assertStatisticsAlmostEqual(
            self.runBacktest(timeseries), [mean, math.sqrt(variance)]
        )

    def test_equal_positive_changes_create_equal_weights(self):
        timeseries = [
            [100.0, 110.0, 132.0],
            [50.0, 55.0, 49.5],
        ]
        # Both stocks gained 10% on day 1, producing 50/50 weights.
        # Their next returns are +20% and -10%, so the portfolio gains 5%.
        returns = [0.0, math.log(1.05)]
        mean = sum(returns) / len(returns)
        variance = sum((value - mean) ** 2 for value in returns) / len(returns)
        self.assertStatisticsAlmostEqual(
            self.runBacktest(timeseries), [mean, math.sqrt(variance)]
        )

    def test_ten_equal_winners_are_equally_diversified(self):
        day_0_prices = [100.0] * 10
        day_1_prices = [110.0] * 10
        day_2_factors = [1.20, 1.15, 1.10, 1.05, 1.00,
                         0.95, 0.90, 0.85, 0.80, 0.75]
        timeseries = [
            [day_0_prices[i], day_1_prices[i], day_1_prices[i] * day_2_factors[i]]
            for i in range(10)
        ]
        # All ten stocks gained 10% on day 1, so each receives 10% of the fund.
        # Their day-2 growth factors average to 0.975.
        returns = [0.0, math.log(0.975)]
        mean = sum(returns) / len(returns)
        variance = sum((value - mean) ** 2 for value in returns) / len(returns)
        self.assertStatisticsAlmostEqual(
            self.runBacktest(timeseries), [mean, math.sqrt(variance)]
        )

    def test_many_stocks_use_uneven_proportional_weights(self):
        day_1_changes = [-0.05, 0.0, 0.01, 0.02, 0.03, 0.04,
                         0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
        day_2_factors = [2.00, 2.00, 1.10, 0.90, 1.20, 0.80,
                         1.05, 0.95, 1.15, 0.85, 1.00, 1.25]
        timeseries = [
            [100.0, 100.0 * (1.0 + change),
             100.0 * (1.0 + change) * factor]
            for change, factor in zip(day_1_changes, day_2_factors)
        ]
        # The first two stocks receive no allocation despite doubling on day 2.
        positive_changes = day_1_changes[2:]
        total_positive_change = sum(positive_changes)
        growth_factor = sum(
            change / total_positive_change * factor
            for change, factor in zip(positive_changes, day_2_factors[2:])
        )
        returns = [0.0, math.log(growth_factor)]
        mean = sum(returns) / len(returns)
        variance = sum((value - mean) ** 2 for value in returns) / len(returns)
        self.assertStatisticsAlmostEqual(
            self.runBacktest(timeseries), [mean, math.sqrt(variance)]
        )

    def test_market_wide_decline_across_twelve_stocks_holds_cash(self):
        timeseries = [
            [100.0 + stock_id, 99.0 + stock_id, 98.0 + stock_id, 97.0 + stock_id]
            for stock_id in range(12)
        ]
        self.assertStatisticsAlmostEqual(
            self.runBacktest(timeseries), [0.0, 0.0]
        )

    def test_rotating_market_leaders_over_multiple_rebalances(self):
        timeseries = [
            [100.0, 110.0, 115.5, 103.95, 103.95, 114.345],
            [50.0, 50.0, 55.0, 60.5, 54.45, 54.45],
            [200.0, 190.0, 209.0, 229.9, 252.89, 240.2455],
        ]
        # Period 1 is cash. Subsequent portfolio factors are:
        # 1.05: stock 0 was the sole day-1 winner;
        # 1.06: day-2 weights were 20%, 40%, 40%;
        # 1.00: equal positions in stocks 1 and 2 offset each other;
        # 0.95: stock 2 was the sole day-4 winner and then lost 5%.
        returns = [0.0, math.log(1.05), math.log(1.06), 0.0, math.log(0.95)]
        mean = sum(returns) / len(returns)
        variance = sum((value - mean) ** 2 for value in returns) / len(returns)
        self.assertStatisticsAlmostEqual(
            self.runBacktest(timeseries), [mean, math.sqrt(variance)]
        )


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
