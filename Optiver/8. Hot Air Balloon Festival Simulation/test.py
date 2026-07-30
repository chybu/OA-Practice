import time
import unittest

from submission import BalloonFestival


class TestBalloonFestival(unittest.TestCase):
    def test_highest_stable_ties_follow_constructor_order(self):
        festival = BalloonFestival(["Bravo", "Alpha", "Charlie"])
        festival.balloon_ascended(1, "Charlie", 1000)
        festival.balloon_ascended(2, "Bravo", 1000)
        festival.balloon_ascended(3, "Alpha", 800)

        self.assertEqual(festival.inspect_balloons(4), ["Bravo", "Charlie"])

    def test_unknown_balloon_actions_fail_without_changing_state(self):
        festival = BalloonFestival(["Known"])
        self.assertFalse(festival.balloon_ascended(1, "Unknown", 100))
        self.assertTrue(festival.balloon_ascended(2, "Known", 100))
        self.assertFalse(festival.balloon_descended(3, "Unknown"))
        self.assertEqual(festival.inspect_balloons(4), ["Known"])

    def test_descending_requires_a_flying_balloon(self):
        festival = BalloonFestival(["A"])
        self.assertFalse(festival.balloon_descended(1, "A"))
        self.assertTrue(festival.balloon_ascended(2, "A", 100))
        self.assertTrue(festival.balloon_descended(3, "A"))
        self.assertFalse(festival.balloon_descended(4, "A"))
        self.assertEqual(festival.inspect_balloons(5), [])

    def test_timestamps_are_globally_strictly_increasing(self):
        festival = BalloonFestival(["A", "B"])
        self.assertTrue(festival.balloon_ascended(10, "A", 100))
        self.assertFalse(festival.set_wind_speed(10, 100, 30))
        self.assertFalse(festival.balloon_ascended(9, "B", 200))
        self.assertEqual(festival.inspect_balloons(10), [])

        # Invalid calls neither alter state nor replace the last timestamp.
        self.assertTrue(festival.balloon_ascended(11, "B", 200))
        self.assertEqual(festival.inspect_balloons(12), ["B"])

    def test_wind_formula_and_contributions_are_additive(self):
        festival = BalloonFestival(["A"])
        # Each center contributes 8 at altitude 100: total wind is 16.
        festival.set_wind_speed(1, 0, 16)
        festival.set_wind_speed(2, 200, 16)
        festival.balloon_ascended(3, "A", 100)
        self.assertEqual(festival.inspect_balloons(4), [])

    def test_exactly_fifteen_is_safe_and_above_fifteen_is_not(self):
        exact = BalloonFestival(["A"])
        exact.set_wind_speed(1, 100, 15)
        exact.balloon_ascended(2, "A", 100)
        self.assertEqual(exact.inspect_balloons(3), ["A"])

        above = BalloonFestival(["A"])
        above.set_wind_speed(1, 100, 15.0001)
        above.balloon_ascended(2, "A", 100)
        self.assertEqual(above.inspect_balloons(3), [])

    def test_same_wind_center_is_overwritten_not_added(self):
        festival = BalloonFestival(["A"])
        festival.set_wind_speed(1, 100, 20)
        festival.set_wind_speed(2, 100, 10)
        festival.balloon_ascended(3, "A", 100)
        self.assertEqual(festival.inspect_balloons(4), ["A"])

    def test_recovery_requires_300_continuous_safe_seconds(self):
        festival = BalloonFestival(["A"])
        festival.set_wind_speed(1, 100, 20)
        festival.balloon_ascended(2, "A", 100)
        festival.set_wind_speed(10, 100, 15)

        self.assertEqual(festival.inspect_balloons(309), [])
        self.assertEqual(festival.inspect_balloons(310), ["A"])

    def test_unsafe_wind_resets_recovery_clock(self):
        festival = BalloonFestival(["A"])
        festival.set_wind_speed(1, 100, 20)
        festival.balloon_ascended(2, "A", 100)
        festival.set_wind_speed(10, 100, 10)
        festival.set_wind_speed(200, 100, 20)
        festival.set_wind_speed(210, 100, 10)

        self.assertEqual(festival.inspect_balloons(310), [])
        self.assertEqual(festival.inspect_balloons(510), ["A"])

    def test_altitude_change_resets_recovery_clock(self):
        festival = BalloonFestival(["A"])
        festival.set_wind_speed(1, 100, 20)
        festival.balloon_ascended(2, "A", 100)
        festival.set_wind_speed(10, 100, 0)
        festival.balloon_ascended(200, "A", 200)

        self.assertEqual(festival.inspect_balloons(310), [])
        self.assertEqual(festival.inspect_balloons(500), ["A"])

    def test_descent_resets_instability_for_future_launch(self):
        festival = BalloonFestival(["A"])
        festival.set_wind_speed(1, 100, 20)
        festival.balloon_ascended(2, "A", 100)
        self.assertEqual(festival.inspect_balloons(3), [])
        self.assertTrue(festival.balloon_descended(4, "A"))

        festival.set_wind_speed(5, 100, 0)
        festival.balloon_ascended(6, "A", 100)
        self.assertEqual(festival.inspect_balloons(7), ["A"])

    def test_highest_altitude_considers_only_stable_balloons(self):
        festival = BalloonFestival(["High", "Low"])
        festival.set_wind_speed(1, 1000, 20)
        festival.balloon_ascended(2, "High", 1000)
        festival.balloon_ascended(3, "Low", 100)
        self.assertEqual(festival.inspect_balloons(4), ["Low"])

    def test_extreme_100000_balloons_with_multiple_wind_centers(self):
        balloon_count = 100_000
        altitude_count = 1_000
        names = [f"balloon-{index:06d}" for index in range(balloon_count)]
        festival = BalloonFestival(names)

        start = time.perf_counter()

        # Even directly at every center, the combined wind cannot exceed 10.
        # All balloons therefore remain stable.
        for index in range(20):
            self.assertTrue(
                festival.set_wind_speed(
                    timestamp=index + 1,
                    centerAltitude=index * 100,
                    windSpeed=0.5,
                )
            )

        wind_end = time.perf_counter()

        for index, name in enumerate(names):
            self.assertTrue(
                festival.balloon_ascended(
                    timestamp=index + 21,
                    name=name,
                    altitude=index % altitude_count,
                )
            )

        ascent_end = time.perf_counter()
        result = festival.inspect_balloons(balloon_count + 21)
        inspect_end = time.perf_counter()

        expected = names[altitude_count - 1 :: altitude_count]
        self.assertEqual(result, expected)

        print(f"\nBalloons:      {balloon_count:,}")
        print(f"Wind centers:  20")
        print(f"Wind setup:    {wind_end - start:.3f} seconds")
        print(f"Ascend time:   {ascent_end - wind_end:.3f} seconds")
        print(f"Inspect time:  {inspect_end - ascent_end:.3f} seconds")
        print(f"Total time:    {inspect_end - start:.3f} seconds")


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)
