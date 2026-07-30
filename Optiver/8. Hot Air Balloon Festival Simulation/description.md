# Hot Air Balloon Festival Simulation

Implement a stateful `BalloonFestival` class that tracks a team's balloons and
determines which are stable under changing wind conditions.

## Class interface

```text
BalloonFestival(balloonNames)
balloon_ascended(timestamp, name, altitude)
balloon_descended(timestamp, name)
set_wind_speed(timestamp, centerAltitude, windSpeed)
inspect_balloons(timestamp)
```

### Constructor

```text
BalloonFestival(balloonNames: list[str])
```

Register the team's unique balloon names in the given order. All balloons
begin on the ground.

### balloon_ascended

```text
balloon_ascended(timestamp, name, altitude) -> bool
```

Move a registered balloon to `altitude`, launching it if necessary, and return
`True`. Return `False` for an unknown name.

A launch starts with default stable state and is immediately checked against
the wind. If the balloon is already flying, the call updates its altitude:

- A stable balloon remains stable unless wind at the new altitude exceeds
  `15`.
- An unstable balloon remains unstable, and changing its altitude resets its
  recovery progress.
- Calling the method with its current altitude does not reset recovery because
  the altitude did not change.

Wind at the resulting altitude is checked immediately.

### balloon_descended

```text
balloon_descended(timestamp, name) -> bool
```

Move a registered flying balloon to the ground and return `True`. Return
`False` if the name is unknown or the balloon is already grounded. Descending
clears its previous stability and recovery state.

### set_wind_speed

```text
set_wind_speed(timestamp, centerAltitude, windSpeed) -> bool
```

Set the wind speed at `centerAltitude` and return `True`. A new value at an
existing center overwrites the old value. Re-evaluate all flying balloons
after the update.

There are two related values:

- **Center wind speed** is the `windSpeed` supplied to this method and stored
  at `centerAltitude`.
- **Total wind at a balloon** is calculated at the balloon's altitude from all
  stored wind centers. It is not another stored center and is not used to
  calculate wind at other altitudes.

A center with stored speed `windSpeed` contributes the following amount at
altitude `h`:

```text
windSpeed / (1 + ((h - centerAltitude) / 100) ** 2)
```

The total wind experienced by a balloon is the sum of these independently
calculated contributions from all centers. Therefore, balloons may be
re-evaluated in any order.

### inspect_balloons

```text
inspect_balloons(timestamp) -> list[str]
```

Return all stable balloons at the greatest altitude occupied by a stable
balloon. Preserve their order from `balloonNames`. Return an empty list if no
stable balloon is flying.

## Stability

- A balloon becomes unstable when its total wind exceeds `15` metres per
  second. Exactly `15` is safe.
- An unstable balloon becomes stable after spending `300` continuous seconds
  at the same altitude with total wind at or below `15`.
- Recovery starts when the wind becomes safe. Wind above `15` or an altitude
  change resets the recovery clock.
- Current wind conditions remain unchanged between timestamped operations.

## Timestamps and invalid operations

Timestamps are numeric seconds and must be globally strictly increasing across
all public method calls. A non-increasing timestamp causes a mutating method to
return `False`, or `inspect_balloons` to return an empty list, without changing
state. Other failed operations also leave state unchanged.

## Input assumptions

```text
balloon names are unique non-empty strings
altitudes and center altitudes are numeric
wind speeds are non-negative numeric values
```

## Example

```text
festival = BalloonFestival(["Aurora", "Comet"])

festival.balloon_ascended(10, "Aurora", 100)
# returns True

festival.balloon_ascended(20, "Comet", 200)
# returns True

festival.inspect_balloons(30)
# returns ["Comet"]

festival.set_wind_speed(40, 200, 20)
# returns True

festival.inspect_balloons(50)
# returns ["Aurora"]
```

## Suggested class signature

```text
class BalloonFestival:
    def __init__(self, balloonNames):
        pass

    def balloon_ascended(self, timestamp, name, altitude):
        pass

    def balloon_descended(self, timestamp, name):
        pass

    def set_wind_speed(self, timestamp, centerAltitude, windSpeed):
        pass

    def inspect_balloons(self, timestamp):
        pass
```
