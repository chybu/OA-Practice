# Event-Driven CPU Overheat Controller

## Problem statement

You are implementing firmware for a multicore processor. Each core runs a
configurable workload that produces heat, every core has its own active-cooling
capacity, and all running cores share a pooled-cooling capacity.

The operating system changes workloads with `SetCoreLoad` and calls `Tick` to
learn which cores have changed between running and shut down.

## Practice thermal model

- At time `0`, every core is running with temperature `0` and load `0`.
- Time and all operation timestamps are measured in whole seconds.
- If `r` cores are running during a second, each running core receives
  `floor(pooledCooling / r)` units of pooled cooling for that second.
- For a running core `i`, its temperature changes during that second by:

  ```text
  load[i] - activeCooling[i] - floor(pooledCooling / r)
  ```

  A core's temperature cannot fall below `0`.
- If a core's temperature reaches or exceeds `shutdownTemperature` at the end
  of a second, it shuts down before the next second. Pooled cooling is then
  redistributed among the remaining running cores.
- A shut-down core does not heat or cool until it is restarted by
  `SetCoreLoad`. Restarting sets its temperature to `0`.

All cores that reach the shutdown temperature at the end of the same second
shut down together. The new pooled-cooling allocation applies from the next
second onward.

## Operations

The arrays `operations` and `operationData` describe calls in non-decreasing
timestamp order. Operations with the same timestamp are processed in array
order.

### SetCoreLoad

Its data has the form:

```text
[timestamp, coreId, watts]
```

First advance the controller to `timestamp`, then set that core's load to
`watts`. If the core is shut down, restart it at temperature `0`.

### Tick

Its data has the form:

```text
[timestamp]
```

Advance the controller to `timestamp`, return the IDs of all cores whose
running/shut-down status changed at least once since the previous `Tick`,
sorted in ascending order, and then clear the change set.

If one core changes status multiple times between two `Tick` calls, include
its ID only once.

Return one row for every `Tick`, in call order.

## Function

Complete `simulateOverheatController` with the following signature:

```text
simulateOverheatController(
    pooledCooling: int,
    coreIds: int[],
    activeCooling: int[],
    shutdownTemperature: int,
    operations: String[],
    operationData: int[][]
) -> int[][]
```

`activeCooling[i]` is the active-cooling capacity of the core identified by
`coreIds[i]`.

## Examples

### Example 1

```text
pooledCooling = 4
coreIds = [10, 20]
activeCooling = [1, 1]
shutdownTemperature = 10
operations = ["SetCoreLoad", "SetCoreLoad", "Tick", "Tick"]
operationData = [[0, 10, 8], [0, 20, 4], [2], [3]]

return [[10], []]
```

While both cores run, each receives `floor(4 / 2) = 2` pooled-cooling units.
Core `10` heats by `8 - 1 - 2 = 5` per second and reaches temperature `10` at
time `2`, so the first `Tick` returns `[10]`.

Core `20` remains running through time `3`, so the second `Tick` returns an
empty row.

### Example 2

```text
pooledCooling = 3
coreIds = [1]
activeCooling = [2]
shutdownTemperature = 5
operations = [
    "SetCoreLoad", "Tick", "SetCoreLoad", "Tick",
    "SetCoreLoad", "Tick", "SetCoreLoad", "Tick"
]
operationData = [
    [0, 1, 6], [1], [1, 1, 0], [3],
    [3, 1, 10], [4], [4, 1, 4], [5]
]

return [[], [], [1], [1]]
```

The first two `Tick` calls observe no status change. After the load becomes
`10`, the core reaches the shutdown temperature at time `4`, so the third row
is `[1]`.

The following `SetCoreLoad` restarts the core at time `4`. The final `Tick`
reports that restart as another status change.

## Constraints

```text
1 <= coreIds.length = activeCooling.length <= 200
all coreIds are distinct
0 <= pooledCooling, activeCooling[i] <= 10^6
1 <= shutdownTemperature <= 10^9
1 <= operations.length = operationData.length <= 2000
coreIds.length * operations.length <= 2 * 10^5
every operation is either SetCoreLoad or Tick
operation timestamps are integers in [0, 10^9] and are non-decreasing
every SetCoreLoad uses a valid core ID and a load in [0, 10^6]
there is at least one Tick operation
```

## Suggested Python signature

```python
def simulateOverheatController(
    pooledCooling,
    coreIds,
    activeCooling,
    shutdownTemperature,
    operations,
    operationData,
):
    pass
```
