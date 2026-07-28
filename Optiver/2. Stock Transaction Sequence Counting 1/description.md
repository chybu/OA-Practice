# Stock Transaction Sequence Counting

A market maker must execute a sequence of buy and sell transactions while
respecting a no-borrowing restriction.

Each transaction involves exactly one share. A buy increases the current stock
position by `1`, while a sell decreases it by `1`. The market maker starts with
no shares and may never hold a negative position.

Given `n`, count the number of distinct transaction sequences containing
exactly `n` buys and `n` sells. Every valid sequence therefore contains `2n`
transactions, starts with position `0`, never causes the position to become
negative, and ends with position `0`.

Two sequences are distinct if a buy or sell occurs at a different transaction
index.

## Task

Complete the function:

```text
countTransactionSequences(n)
```

The function must return the number of valid transaction sequences.

## Input

```text
n: an integer
```

`n` is the required number of buy transactions and also the required number of
sell transactions.

## Output

Return an integer representing the number of distinct valid sequences of `2n`
transactions.

## Constraints

```text
0 <= n <= 35
```

The result fits in a signed 64-bit integer.

## Examples

### Example 1

```text
n = 2
```

There are two valid sequences:

```text
buy, sell, buy, sell
buy, buy, sell, sell
```

The function returns:

```text
2
```

### Example 2

```text
n = 3
```

The five valid sequences are:

```text
buy, buy, buy, sell, sell, sell
buy, buy, sell, buy, sell, sell
buy, buy, sell, sell, buy, sell
buy, sell, buy, buy, sell, sell
buy, sell, buy, sell, buy, sell
```

The function returns:

```text
5
```