# Squirrel Nut Storage Tracker

Researchers study how squirrels hide and retrieve nuts from cone-shaped storage
locations. Each location contains several levels with different capacities.

Implement a stateful `SquirrelResearch` class that manages the locations,
tracks hidden nuts, applies expiration rules, and returns nuts in the required
retrieval order.

All operation timestamps are globally strictly increasing. Timestamps are
floating-point seconds since the Unix epoch, and nut weights are floating-point
values measured in grams.

## Storage locations

The constructor receives a mapping from each location ID to its number of
levels.

Levels are numbered from deepest to topmost, starting at `0`. Their capacities
follow this sequence:

```text
1, 2, 3, 5, 8, 13, ...
```

Therefore:

```text
capacity[0] = 1
capacity[1] = 2
capacity[i] = capacity[i - 1] + capacity[i - 2], for i >= 2
```

For example, a location with three levels has capacities `1`, `2`, and `3`,
for a total capacity of `6` nuts.

## Class interface

Implement:

```text
SquirrelResearch(locations)
HideNut(timestamp, location_id, nut_id, nut_weight, time_to_expire)
RetrieveNuts(timestamp, location_id, max_squirrel_capacity_in_nuts)
```

### Constructor

```text
SquirrelResearch(locations: dict[str, int])
```

`locations` maps each location ID to the number of levels in that location.
Every location begins empty.

### HideNut

```text
HideNut(
    timestamp,
    location_id,
    nut_id,
    nut_weight,
    time_to_expire
) -> bool
```

Attempt to hide one nut and return `True` if successful.

Nuts are placed in the deepest level that is not full. A higher level may be
used only after every deeper level has reached its capacity.

The operation returns `False` without changing any state when:

- `location_id` does not identify a configured location.
- The location is full.
- `nut_id` is already being used by a nut hidden at any location.

On success, the nut expires immediately after:

```text
timestamp + time_to_expire
```

Consequently, the nut remains valid at exactly that timestamp and is expired
when a later retrieval timestamp is greater than its expiration timestamp.
Expired nuts continue occupying storage until encountered during retrieval.

After a nut has been retrieved or discarded, its ID is no longer active and
may be reused by a later `HideNut` operation.

### RetrieveNuts

```text
RetrieveNuts(
    timestamp,
    location_id,
    max_squirrel_capacity_in_nuts
) -> list[str]
```

Retrieve up to `max_squirrel_capacity_in_nuts` non-expired nuts and return their
IDs in retrieval order.

Return an empty list when the location is invalid, the location contains no
nuts, or the squirrel's capacity is `0`.

The next nut is selected by repeatedly applying the following rules.

1. Find the topmost level that currently contains at least one nut. That level
   is reachable.
2. Find the topmost occupied level. If it contains strictly less than 50% of its capacity, the level immediately below it also becomes reachable.
3. Among all nuts in the reachable level or levels, select the nut with the
   greatest weight. If weights are equal, select the alphabetically smallest
   nut ID.
4. Remove the selected nut.
5. If the nut came from a level below the topmost occupied level, move the
   lightest nut from the level immediately above into the newly freed slot. If
   several nuts share the lightest weight, move the alphabetically smallest ID.
6. If the selected nut is expired at the retrieval timestamp, discard it and
   do not include its ID in the result. A discarded nut does not consume the
   squirrel's carrying capacity.
7. Recalculate the topmost occupied level and reachable levels before choosing
   another nut.

Retrieval stops when one of the following occurs:

- The returned list contains `max_squirrel_capacity_in_nuts` IDs.
- The location contains no more nuts.
- No further nut is reachable under the rules above.

Every retrieved or discarded nut is removed from the global active-ID set.

## Input assumptions

```text
location IDs are non-empty strings and are unique
nut IDs are non-empty strings
number of levels in each location >= 1
nut_weight > 0
time_to_expire >= 0
max_squirrel_capacity_in_nuts >= 0
operation timestamps are globally strictly increasing
```

## Example 1

```text
research = SquirrelResearch({"oak": 1})

research.HideNut(1000.0, "oak", "nutA", 12.5, 60.0)
# returns True

research.RetrieveNuts(1010.0, "oak", 1)
# returns ["nutA"]
```

### Example 2: Expiration and global nut IDs

```text
research = SquirrelResearch({"oak": 1, "pine": 1})

research.HideNut(2000.0, "oak", "nutB", 9.0, 5.0)
# returns True; nutB expires immediately after timestamp 2005.0

research.HideNut(2001.0, "pine", "nutB", 11.0, 20.0)
# returns False because nutB is still hidden at oak

research.RetrieveNuts(2006.0, "oak", 1)
# returns []; the expired nutB is discarded and removed

research.HideNut(2007.0, "pine", "nutB", 11.0, 20.0)
# returns True because the discarded ID may now be reused
```

## Suggested class signature

```text
class SquirrelResearch:
    def __init__(self, locations):
        # Initialize all locations.
        pass

    def HideNut(
        self,
        timestamp,
        location_id,
        nut_id,
        nut_weight,
        time_to_expire,
    ):
        # Attempt to hide one nut.
        pass

    def RetrieveNuts(
        self,
        timestamp,
        location_id,
        max_squirrel_capacity_in_nuts,
    ):
        # Retrieve nuts in the required order.
        pass
```
