import time
import unittest

from submission import SquirrelResearch


class TestSquirrelResearch(unittest.TestCase):
    def test_hide_and_retrieve_single_nut(self):
        research = SquirrelResearch({"oak": 1})

        self.assertTrue(research.HideNut(1000.0, "oak", "nutA", 12.5, 60.0))
        self.assertEqual(research.RetrieveNuts(1010.0, "oak", 1), ["nutA"])

    def test_invalid_location(self):
        research = SquirrelResearch({"oak": 1})

        self.assertFalse(research.HideNut(1.0, "pine", "nutA", 10.0, 20.0))
        self.assertEqual(research.RetrieveNuts(2.0, "pine", 1), [])

    def test_level_capacities_and_deepest_first_placement(self):
        research = SquirrelResearch({"oak": 4})
        levels = research.location_dic["oak"]

        self.assertEqual([level.max_size for level in levels], [1, 2, 3, 5])

        for index in range(7):
            self.assertTrue(
                research.HideNut(
                    float(index + 1), "oak", f"nut{index}", index + 1.0, 100.0
                )
            )

        self.assertEqual([level.size for level in levels], [1, 2, 3, 1])

    def test_full_location_rejects_nut_without_changing_state(self):
        research = SquirrelResearch({"oak": 2})

        self.assertTrue(research.HideNut(1.0, "oak", "a", 1.0, 100.0))
        self.assertTrue(research.HideNut(2.0, "oak", "b", 2.0, 100.0))
        self.assertTrue(research.HideNut(3.0, "oak", "c", 3.0, 100.0))
        self.assertFalse(research.HideNut(4.0, "oak", "d", 4.0, 100.0))

        self.assertEqual([level.size for level in research.location_dic["oak"]], [1, 2])
        self.assertNotIn("d", research.nuts_set)

    def test_nut_ids_are_globally_unique_while_active(self):
        research = SquirrelResearch({"oak": 1, "pine": 1})

        self.assertTrue(research.HideNut(1.0, "oak", "shared", 5.0, 100.0))
        self.assertFalse(research.HideNut(2.0, "pine", "shared", 7.0, 100.0))
        self.assertEqual(research.RetrieveNuts(3.0, "pine", 1), [])

    def test_retrieval_prefers_greatest_weight(self):
        research = SquirrelResearch({"oak": 2})
        research.HideNut(1.0, "oak", "deep-heavy", 100.0, 100.0)
        research.HideNut(2.0, "oak", "top-light", 1.0, 100.0)

        # The top level is exactly 50% full, so the deeper nut is not reachable.
        self.assertEqual(research.RetrieveNuts(3.0, "oak", 1), ["top-light"])
        self.assertEqual(research.RetrieveNuts(4.0, "oak", 1), ["deep-heavy"])

    def test_equal_weights_use_alphabetically_smallest_id(self):
        research = SquirrelResearch({"oak": 2})
        research.HideNut(1.0, "oak", "deep", 1.0, 100.0)
        research.HideNut(2.0, "oak", "z-nut", 10.0, 100.0)
        research.HideNut(3.0, "oak", "a-nut", 10.0, 100.0)

        self.assertEqual(
            research.RetrieveNuts(4.0, "oak", 2), ["a-nut", "z-nut"]
        )

    def test_below_top_becomes_reachable_and_causes_redistribution(self):
        research = SquirrelResearch({"oak": 3})
        research.HideNut(1.0, "oak", "level0", 1.0, 100.0)
        research.HideNut(2.0, "oak", "level1-heavy", 9.0, 100.0)
        research.HideNut(3.0, "oak", "level1-light", 2.0, 100.0)
        research.HideNut(4.0, "oak", "level2", 5.0, 100.0)

        # Level 2 has 1/3 slots occupied, so level 1 is also reachable.
        self.assertEqual(
            research.RetrieveNuts(5.0, "oak", 1), ["level1-heavy"]
        )

        levels = research.location_dic["oak"]
        self.assertEqual([level.size for level in levels], [1, 2, 0])
        self.assertEqual(
            research.RetrieveNuts(6.0, "oak", 1), ["level2"]
        )

    def test_expired_nuts_are_discarded_without_using_capacity(self):
        research = SquirrelResearch({"oak": 2})
        research.HideNut(1.0, "oak", "deep-valid", 1.0, 100.0)
        research.HideNut(2.0, "oak", "expired", 10.0, 1.0)
        research.HideNut(3.0, "oak", "valid", 5.0, 100.0)

        self.assertEqual(research.RetrieveNuts(4.0, "oak", 1), ["valid"])
        self.assertNotIn("expired", research.nuts_set)
        self.assertIn("deep-valid", research.nuts_set)

    def test_nut_is_valid_at_exact_expiration_timestamp(self):
        research = SquirrelResearch({"oak": 1})
        research.HideNut(10.0, "oak", "nut", 1.0, 5.0)

        self.assertEqual(research.RetrieveNuts(15.0, "oak", 1), ["nut"])

    def test_retrieved_or_discarded_id_can_be_reused(self):
        research = SquirrelResearch({"oak": 1, "pine": 1})
        research.HideNut(1.0, "oak", "reusable", 1.0, 1.0)

        self.assertEqual(research.RetrieveNuts(3.0, "oak", 1), [])
        self.assertTrue(research.HideNut(4.0, "pine", "reusable", 2.0, 10.0))
        self.assertEqual(research.RetrieveNuts(5.0, "pine", 1), ["reusable"])
        self.assertTrue(research.HideNut(6.0, "oak", "reusable", 3.0, 10.0))

    def test_zero_retrieval_capacity_does_not_change_state(self):
        research = SquirrelResearch({"oak": 1})
        research.HideNut(1.0, "oak", "nut", 1.0, 100.0)

        self.assertEqual(research.RetrieveNuts(2.0, "oak", 0), [])
        self.assertIn("nut", research.nuts_set)
        self.assertEqual(research.location_dic["oak"][0].size, 1)

    def test_extreme_100000_nuts(self):
        nut_count = 100_000
        research = SquirrelResearch({"giant-tree": 25})

        start = time.perf_counter()

        for index in range(nut_count):
            success = research.HideNut(
                timestamp=float(index),
                location_id="giant-tree",
                nut_id=f"nut-{index:06d}",
                nut_weight=float((index * 7919) % 10_000 + 1),
                time_to_expire=1_000_000_000.0,
            )
            self.assertTrue(success, f"HideNut failed at index {index}")

        hide_end = time.perf_counter()

        retrieved = research.RetrieveNuts(
            timestamp=float(nut_count + 1),
            location_id="giant-tree",
            max_squirrel_capacity_in_nuts=nut_count,
        )

        retrieve_end = time.perf_counter()

        self.assertEqual(len(retrieved), nut_count)
        self.assertEqual(len(set(retrieved)), nut_count)
        self.assertFalse(research.nuts_set)
        self.assertEqual(
            research.RetrieveNuts(float(nut_count + 2), "giant-tree", 1), []
        )

        print(f"\nNuts:          {nut_count:,}")
        print(f"Hide time:     {hide_end - start:.3f} seconds")
        print(f"Retrieve time: {retrieve_end - hide_end:.3f} seconds")
        print(f"Total time:    {retrieve_end - start:.3f} seconds")


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)
