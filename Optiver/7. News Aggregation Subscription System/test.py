import time
import unittest

from submission import NewsProvider


class TestNewsProvider(unittest.TestCase):
    def setUp(self):
        self.provider = NewsProvider()

    def test_basic_matching_delivery_and_no_duplicate_delivery(self):
        self.assertTrue(
            self.provider.AddSubscription(10, 50, 2, ["markets", "technology"])
        )
        self.assertTrue(
            self.provider.NewsReceived(101, 1000.0, 75, ["markets"])
        )

        self.assertEqual(self.provider.Publish(1000.5, 10.0), {101: [10]})
        self.assertEqual(self.provider.Publish(1000.8, 10.0), {})

    def test_remove_unknown_fails_and_existing_subscription_is_removed(self):
        self.assertFalse(self.provider.RemoveSubscription(7))
        self.provider.AddSubscription(7, 0, 10, ["world"])
        self.assertTrue(self.provider.RemoveSubscription(7))
        self.assertFalse(self.provider.RemoveSubscription(7))
        self.provider.NewsReceived(1, 1.0, 100, ["world"])
        self.assertEqual(self.provider.Publish(2.0, 10.0), {})

    def test_duplicate_news_id_is_rejected_and_original_is_unchanged(self):
        self.provider.AddSubscription(1, 50, 10, ["a"])
        self.assertTrue(self.provider.NewsReceived(99, 1.0, 10, ["b"]))
        self.assertFalse(self.provider.NewsReceived(99, 2.0, 100, ["a"]))
        self.assertEqual(self.provider.Publish(3.0, 10.0), {})

    def test_topic_and_interest_filters(self):
        self.provider.AddSubscription(1, 50, 10, ["a", "b"])
        self.provider.NewsReceived(1, 1.0, 100, ["c"])
        self.provider.NewsReceived(2, 2.0, 49, ["a"])
        self.provider.NewsReceived(3, 3.0, 50, ["b", "c"])

        self.assertEqual(self.provider.Publish(4.0, 10.0), {3: [1]})

    def test_max_age_is_inclusive_and_future_news_is_not_eligible(self):
        self.provider.AddSubscription(1, 0, 10, ["a"])
        self.provider.NewsReceived(1, 5.0, 1, ["a"])
        self.provider.NewsReceived(2, 10.001, 2, ["a"])

        self.assertEqual(self.provider.Publish(10.0, 5.0), {1: [1]})

    def test_priority_prefers_highest_interest(self):
        self.provider.AddSubscription(1, 0, 1, ["a"])
        self.provider.NewsReceived(10, 5.0, 80, ["a"])
        self.provider.NewsReceived(11, 1.0, 90, ["a"])

        self.assertEqual(self.provider.Publish(5.0, 10.0), {11: [1]})

    def test_priority_prefers_oldest_timestamp_when_interest_ties(self):
        self.provider.AddSubscription(1, 0, 1, ["a"])
        self.provider.NewsReceived(11, 2.0, 90, ["a"])
        self.provider.NewsReceived(12, 1.0, 90, ["a"])

        self.assertEqual(self.provider.Publish(5.0, 10.0), {12: [1]})

    def test_priority_prefers_highest_id_when_other_keys_tie(self):
        self.provider.AddSubscription(1, 0, 1, ["a"])
        self.provider.NewsReceived(11, 1.0, 90, ["a"])
        self.provider.NewsReceived(12, 1.0, 90, ["a"])

        self.assertEqual(self.provider.Publish(5.0, 10.0), {12: [1]})

    def test_rate_limit_is_independent_for_each_subscriber(self):
        self.provider.AddSubscription(1, 0, 1, ["a"])
        self.provider.AddSubscription(2, 0, 2, ["a"])
        self.provider.NewsReceived(1, 1.0, 20, ["a"])
        self.provider.NewsReceived(2, 2.0, 10, ["a"])

        self.assertEqual(
            self.provider.Publish(3.0, 10.0),
            {1: [1, 2], 2: [2]},
        )

    def test_rate_limit_uses_rolling_window_and_defers_news(self):
        self.provider.AddSubscription(1, 0, 1, ["a"])
        self.provider.NewsReceived(1, 1.0, 20, ["a"])
        self.provider.NewsReceived(2, 2.0, 10, ["a"])

        self.assertEqual(self.provider.Publish(3.0, 10.0), {1: [1]})
        self.assertEqual(self.provider.Publish(3.999, 10.0), {})
        self.assertEqual(self.provider.Publish(4.0, 10.0), {2: [1]})

    def test_zero_rate_limit_never_publishes(self):
        self.provider.AddSubscription(1, 0, 0, ["a"])
        self.provider.NewsReceived(1, 1.0, 1, ["a"])
        self.assertEqual(self.provider.Publish(2.0, 10.0), {})

    def test_update_changes_filters_but_preserves_delivery_history(self):
        self.provider.AddSubscription(1, 0, 10, ["old"])
        self.provider.NewsReceived(1, 1.0, 10, ["old", "new"])
        self.assertEqual(self.provider.Publish(2.0, 10.0), {1: [1]})

        self.assertTrue(self.provider.AddSubscription(1, 5, 10, ["new"]))
        self.provider.NewsReceived(2, 2.1, 4, ["new"])
        self.provider.NewsReceived(3, 2.2, 5, ["new"])

        self.assertEqual(self.provider.Publish(3.1, 10.0), {3: [1]})

    def test_update_preserves_recent_rate_limit_history(self):
        self.provider.AddSubscription(1, 0, 1, ["a"])
        self.provider.NewsReceived(1, 1.0, 2, ["a"])
        self.provider.NewsReceived(2, 1.1, 1, ["a"])
        self.assertEqual(self.provider.Publish(2.0, 10.0), {1: [1]})

        self.provider.AddSubscription(1, 0, 2, ["a"])
        self.assertEqual(self.provider.Publish(2.5, 10.0), {2: [1]})

    def test_remove_then_readd_starts_fresh_subscription_state(self):
        self.provider.AddSubscription(1, 0, 1, ["a"])
        self.provider.NewsReceived(1, 1.0, 1, ["a"])
        self.assertEqual(self.provider.Publish(2.0, 10.0), {1: [1]})

        self.provider.RemoveSubscription(1)
        self.provider.AddSubscription(1, 0, 1, ["a"])
        self.assertEqual(self.provider.Publish(2.1, 10.0), {1: [1]})

    def test_result_omits_undelivered_news_and_sorts_subscriber_ids(self):
        self.provider.AddSubscription(20, 0, 10, ["a"])
        self.provider.AddSubscription(3, 0, 10, ["a"])
        self.provider.AddSubscription(11, 100, 10, ["a"])
        self.provider.NewsReceived(5, 1.0, 10, ["a"])
        self.provider.NewsReceived(6, 1.0, 10, ["other"])

        self.assertEqual(self.provider.Publish(2.0, 10.0), {5: [3, 20]})

    def test_old_deferred_news_can_expire_without_being_delivered(self):
        self.provider.AddSubscription(1, 0, 1, ["a"])
        self.provider.NewsReceived(1, 1.0, 100, ["a"])
        self.provider.NewsReceived(2, 1.5, 1, ["a"])
        self.assertEqual(self.provider.Publish(2.0, 10.0), {1: [1]})
        self.assertEqual(self.provider.Publish(3.0, 1.0), {})

    def test_extreme_100000_news_for_one_subscriber(self):
        news_count = 100_000
        subscriber_id = 1
        topic = "markets"

        self.provider.AddSubscription(
            subscriber_id,
            minInterest=0,
            maxNewsPerSecond=news_count,
            topics=[topic],
        )

        start = time.perf_counter()

        for news_id in range(news_count):
            self.assertTrue(
                self.provider.NewsReceived(
                    id=news_id,
                    timestamp=1.0,
                    interest=100,
                    topics=[topic],
                )
            )

        receive_end = time.perf_counter()
        result = self.provider.Publish(timestamp=2.0, maxAge=10.0)
        publish_end = time.perf_counter()

        self.assertEqual(len(result), news_count)
        self.assertEqual(set(result), set(range(news_count)))
        self.assertTrue(
            all(ids == [subscriber_id] for ids in result.values())
        )

        # Every item was already delivered, so publishing again sends nothing.
        self.assertEqual(self.provider.Publish(timestamp=3.0, maxAge=10.0), {})

        print(f"\nNews items:  {news_count:,}")
        print(f"Receive time: {receive_end - start:.3f} seconds")
        print(f"Publish time: {publish_end - receive_end:.3f} seconds")
        print(f"Total time:   {publish_end - start:.3f} seconds")


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)
