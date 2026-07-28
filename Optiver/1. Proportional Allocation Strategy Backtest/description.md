# Proportional Allocation Strategy Backtest

A fund uses recent stock performance to determine its daily portfolio allocation.

At the end of each day, the fund calculates each stock’s percentage price change from the previous day. Stocks with a positive price change are selected for investment. The portfolio is allocated among the selected stocks in proportion to their percentage changes.

Stocks whose prices decreased or remained unchanged receive no allocation. If no stock had a positive price change, the entire portfolio remains in cash. Cash does not earn interest.

The allocation calculated at the end of a day is held until the end of the following day, at which point the portfolio is rebalanced again.

The fund begins with `$1,000,000` in cash. Since no previous price information is available on day `0`, it remains in cash during the first period.

Fractional shares may be traded, and there are no transaction costs.

## Task

Complete the function:

```text
BacktestStatistics(timeseries)
```

The function must return two values:

```text
[mean, standardDeviation]
```

where:

- `mean` is the average of the portfolio’s daily log returns.
- `standardDeviation` is the population standard deviation of those daily log returns.

A portfolio’s daily log return is the natural logarithm of the current portfolio value divided by its value on the previous day.

Include all consecutive daily periods in the calculation, including the initial period in which the portfolio remains in cash.

## Input

```text
timeseries: a two-dimensional array of doubles
```

`timeseries[i][j]` represents the end-of-day price of stock `i` on day `j`.

All stocks have prices for the same number of days.

## Output

Return a two-element array of doubles:

```text
[average daily log return, standard deviation of daily log returns]
```

## Constraints

```text
1 ≤ number of stocks ≤ 100
2 ≤ number of days ≤ 10,000
0 < timeseries[i][j] ≤ 10^6
```

## Examples

Stocks A and B with a starting
portfolio value of `$1,000,000`:

```text
timeseries = [
    [100.0, 115.0, 117.3],
    [200.0, 210.0, 199.5]
]
```

- **Day 0:** A = `$100`, B = `$200`. Their returns are not yet known because
  there are no previous prices, so the fund stays in cash.
- **Day 1:** A = `$115` (`+15%`), B = `$210` (`+5%`). The combined positive
  change is `20%`, so the fund allocates `15/20 = 3/4` to A (`$750,000`) and
  `5/20 = 1/4` to B (`$250,000`). The portfolio is still worth `$1,000,000`
  immediately after this rebalance.
- **Day 2:** A = `$117.30` (`+2%`), B = `$199.50` (`-5%`). The A position is
  worth `$765,000`, and the B position is worth `$237,500`, making the total
  portfolio value `$1,002,500`. Because only A had a positive return during
  this period, the fund sells B and reallocates the full `$1,002,500` to A for
  the following period.

There are three days and therefore two daily log returns: `0` for the initial
cash period and `ln(1,002,500 / 1,000,000) = ln(1.0025)` for the second period.

The function returns the mean and population standard deviation of the portfolio’s two daily log returns.

## Function signature

```text
# Complete the 'BacktestStatistics' function below.
#
# The function is expected to return a DOUBLE_ARRAY.
# The function accepts a DOUBLE_2D_ARRAY timeseries as parameter.
#

def BacktestStatistics(timeseries):
    # Write your code here
```
