# Variable-Size Stock Order Sequence Counting

A market maker wants to buy exactly `n` shares of a stock. Each order must use
one of the permitted order sizes in `k`.

All permitted order sizes are distinct positive integers. An order sequence is
valid when the sum of its order sizes is exactly `n`.

The order of the transactions matters. For example, `[1, 2]` and `[2, 1]` are
different sequences even though both purchase the same total number of shares.
An order size may be used any number of times.

## Task

Complete the function:

```text
countTransactionSequences(n, k)
```

The function must return the number of ordered sequences of permitted order
sizes whose sum is exactly `n`.

## Input

```text
n: an integer
k: an array of integers
```

where:

- `n` is the target number of shares.
- `k` contains the permitted order sizes.

## Output

Return an integer representing the number of distinct ordered sequences that
sum to `n`.

Return `0` when the target cannot be reached using the permitted order sizes.

## Constraints

```text
n >= 0
1 <= length of k
k[i] > 0
k[i] != k[j] for i != j
```

## Examples

### Example 1

```text
n = 3
k = [1, 2]
```

There are three valid sequences:

```text
[1, 1, 1]
[1, 2]
[2, 1]
```

The function returns:

```text
3
```

### Example 2

```text
n = 3
k = [2, 4]
```

No sequence of permitted order sizes sums to `3`, so the function returns:

```text
0
```

### Example 3

```text
n = 0
k = [1, 2]
```

There is one valid sequence: the empty sequence. It contains no orders and has
a total size of `0`.

The function returns:

```text
1
```
