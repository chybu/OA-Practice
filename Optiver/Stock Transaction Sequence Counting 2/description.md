# Bounded Stock Transaction Sequence Counting

A market maker starts with `k` shares of a stock and wants to finish with
exactly `n` shares.

Each transaction involves exactly one share. A buy increases the current stock
position by `1`, while a sell decreases it by `1`. The stock cannot be borrowed,
so the position may never become negative.

The market maker may perform any number of transactions from `0` through `m`,
inclusive. Count the distinct buy and sell sequences that end with exactly `n`
shares while respecting the no-borrowing restriction after every transaction.

Two sequences are distinct if they contain different numbers of transactions,
or if a buy or sell occurs at a different transaction index.

## Task

Complete the function:

```text
countTransactionSequences(n, k, m)
```

The function must return the number of valid transaction sequences containing
at most `m` transactions.

## Input

```text
n: an integer
k: an integer
m: an integer
```

where:

- `n` is the target number of shares.
- `k` is the initial number of shares.
- `m` is the maximum number of transactions allowed.

## Output

Return an integer representing the number of distinct valid transaction
sequences that finish with exactly `n` shares.

## Constraints

```text
n >= 0
k >= 0
m >= 0
```

## Examples

### Example 1

```text
n = 2
k = 1
m = 3
```

There are four valid sequences:

```text
buy
buy, sell, buy
buy, buy, sell
sell, buy, buy
```

Each sequence starts with `1` share, never produces a negative position, uses
at most `3` transactions, and finishes with `2` shares.

The function returns:

```text
4
```

### Example 2

```text
n = 0
k = 0
m = 2
```

There are two valid sequences:

```text
an empty sequence
buy, sell
```

The function returns:

```text
2
```