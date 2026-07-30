# News Aggregation / Subscription System

An electronic news provider receives stories continuously from reporters and
external newswires. Each story is tagged with one or more topics, such as
`"markets"`, `"technology"`, or `"sports"`, and is assigned an interest score
that indicates its importance.

Customers subscribe to the topics they care about. Each customer also chooses
a minimum interest score, so routine stories can be ignored, and a maximum
delivery rate, so they are not overwhelmed by too many alerts in a short
period.

Stories are recorded as soon as they arrive, but they are delivered only when
the provider performs a publishing cycle. During that cycle, the provider must
match stories to customers, ignore stories that have become too old, respect
each customer's delivery limit, and send the most important eligible stories
first. A customer must never receive the same story twice.

Implement a stateful `NewsProvider` class that performs this subscription,
ingestion, and publishing process.

Timestamps are floating-point seconds since the Unix epoch and may have
millisecond precision. Calls to `Publish` use strictly increasing timestamps.

## Class interface

Implement:

```text
NewsProvider()
AddSubscription(id, minInterest, maxNewsPerSecond, topics)
RemoveSubscription(id)
NewsReceived(id, timestamp, interest, topics)
Publish(timestamp, maxAge)
```

Subscriber IDs and news IDs are integers. Interests and rate limits are
non-negative integers. Topics are non-empty strings.

### AddSubscription

```text
AddSubscription(
    id: int,
    minInterest: int,
    maxNewsPerSecond: int,
    topics: list[str]
) -> bool
```

Register a subscription and return `True`. A subscription is interested in the
set of topics supplied by `topics`; duplicate topic names have no additional
effect.

If the subscriber ID already exists, update its minimum interest, rate limit,
and topics, then return `True`. Updating a subscription does not erase its
delivery history: news already delivered to that subscriber must not be sent
again, and recent deliveries still count toward its rolling rate limit.

### RemoveSubscription

```text
RemoveSubscription(id: int) -> bool
```

Remove an existing subscription and return `True`. Return `False` if the ID is
not currently registered.

Removing a subscription removes all of its state. If the same subscriber ID is
later added again, it is a new subscription with no delivery or rate-limit
history.

### NewsReceived

```text
NewsReceived(
    id: int,
    timestamp: float,
    interest: int,
    topics: list[str]
) -> bool
```

Record a news item and return `True`. Return `False` without changing state if
the news ID has ever been used before. News IDs remain reserved even after the
item becomes too old to publish.

### Publish

```text
Publish(timestamp: float, maxAge: float) -> dict[int, list[int]]
```

Return the deliveries made by this call. Each key is a news ID and its value is
the list of subscriber IDs that receive that news item. Do not include news
items delivered to no subscribers. Subscriber IDs in each returned list must
be in ascending numeric order.

A news item is eligible for a subscriber only when all of the following hold:

- The subscriber is currently registered.
- The subscriber and news item share at least one topic.
- The news interest is at least the subscriber's `minInterest`.
- The news timestamp is not in the future.
- Its age, `timestamp - news_timestamp`, is at most `maxAge`.
- That subscriber has not received that news item before.
- Sending it would not exceed the subscriber's rolling rate limit.

For each subscriber, consider eligible undelivered items in this priority
order:

1. Higher interest first.
2. For equal interest, older news timestamp first.
3. For equal interest and timestamp, higher news ID first.

Each subscriber has a separate delivery limit. `maxNewsPerSecond` is the most
news that subscriber may receive during the one second immediately before and
including the current `Publish` time.

For example, suppose a subscriber has a limit of `2`:

- If two stories are delivered at time `10.0`, no more can be delivered to that
  subscriber at time `10.5`.
- At time `11.0`, those two deliveries are exactly one second old, so they no
  longer count. The subscriber may receive stories again.

Every story delivered during a `Publish` call is considered delivered at that
call's timestamp. A limit of `0` means that the subscriber cannot receive any
stories.

Reaching the limit postpones a story; it does not mark the story as delivered.
A later `Publish` call may still deliver it after space becomes available,
provided the story is not too old under that later call's `maxAge`.

## Input assumptions

The following constraints are guaranteed:

```text
subscriber IDs and news IDs are integers
minInterest >= 0
maxNewsPerSecond >= 0
interest >= 0
maxAge >= 0
topic collections contain valid non-empty strings
news timestamps have millisecond precision
Publish timestamps are strictly increasing
```

## Example

```text
provider = NewsProvider()

provider.AddSubscription(10, 50, 2, ["markets", "technology"])
# returns True

provider.NewsReceived(101, 1000.0, 75, ["markets"])
# returns True

provider.Publish(1000.5, 10.0)
# returns {101: [10]}

provider.Publish(1000.8, 10.0)
# returns {}; subscriber 10 never receives news 101 twice
```

## Suggested class signature

```text
class NewsProvider:
    def __init__(self):
        pass

    def AddSubscription(self, id, minInterest, maxNewsPerSecond, topics):
        pass

    def RemoveSubscription(self, id):
        pass

    def NewsReceived(self, id, timestamp, interest, topics):
        pass

    def Publish(self, timestamp, maxAge):
        pass
```
