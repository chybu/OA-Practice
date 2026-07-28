# Build Binary Tree from Edges / S-Expression

You are given a collection of directed parent-child pairs describing a binary
tree. Each pair is supplied as a raw string and must be validated before the
tree is built.

A valid pair has the exact form:

```text
(P,C)
```

where `P` and `C` are uppercase English letters from `A` through `Z`. `P` is
the parent and `C` is the child. No spaces or additional characters are allowed
inside a pair string.

If the input describes a valid binary tree, return its S-expression. Otherwise,
return the highest-priority applicable error code.

## Task

Complete the function:

```text
buildSExpression(pairs)
```

The function must validate the input, build the tree when possible, and return
either its S-expression or an error code.

## Error priority

Errors must be checked in the following order. If more than one error applies,
return the error with the smallest number.

```text
E1: Invalid Input String
E2: Duplicate Pair
E3: A Parent Has More Than Two Children
E4: Multiple Roots
E5: Cycle in the Tree
```

The errors are defined as follows:

- **E1 — Invalid Input String:** The input is empty, or at least one element
  does not exactly match `(P,C)` with two uppercase letters. Examples include
  `A,B`, `(A, B)`, `(AA,B)`, `(a,B)`, and `(A,B)extra`.
- **E2 — Duplicate Pair:** The same directed parent-child pair appears more
  than once.
- **E3 — A Parent Has More Than Two Children:** A node has more than two
  distinct direct children.
- **E4 — Multiple Roots:** The edges do not form one connected rooted
  structure. This includes having more than one root or assigning the same
  child to more than one parent.
- **E5 — Cycle in the Tree:** Following child edges can return to a node that
  is already on the current path. A self-edge such as `(A,A)` is also a cycle.

Complete all checks needed for a higher-priority error before returning a
lower-priority error.

## S-expression

For a valid tree, define the S-expression recursively as:

```text
S(node) = "(" + node.value + S(first child) + S(second child) + ")"
```

The children of each node are ordered lexicographically by their values. A leaf
has no child expressions, so a leaf containing `C` is written as `(C)`.

## Input

```text
pairs: an array of strings
```

Each `pairs[i]` is intended to describe one directed parent-child edge.

## Output

Return a string containing either:

- The S-expression of the valid binary tree, or
- One of `E1`, `E2`, `E3`, `E4`, or `E5`.

## Constraints

```text
1 <= length of pairs
Each valid node value is an uppercase letter from A through Z
```

## Examples

### Example 1: Valid tree

```text
pairs = ["(A,B)", "(B,C)", "(A,D)"]
```

The tree has root `A`. Its children are `B` and `D`, and `B` has child `C`.
The function returns:

```text
(A(B(C))(D))
```

### Example 2: Invalid input string

```text
pairs = ["(A,B)", "A,C"]
```

`A,C` does not have the required pair format. The function returns:

```text
E1
```

### Example 3: Duplicate pair

```text
pairs = ["(A,B)", "(A,B)"]
```

The function returns:

```text
E2
```

### Example 4: Too many children

```text
pairs = ["(A,B)", "(A,C)", "(A,D)"]
```

Node `A` has three children. The function returns:

```text
E3
```

### Example 5: Multiple roots

```text
pairs = ["(A,B)", "(C,D)"]
```

Both `A` and `C` are roots of separate components. The function returns:

```text
E4
```

### Example 6: Cycle

```text
pairs = ["(A,B)", "(B,C)", "(C,A)"]
```

The edges form the cycle `A -> B -> C -> A`. The function returns:

```text
E5
```

### Example 7: Error priority

```text
pairs = ["(A,B)", "(A,B)", "(A,C)", "(A,D)"]
```

The input contains both a duplicate pair and a parent with more than two
children. Because `E2` has higher priority than `E3`, the function returns:

```text
E2
```