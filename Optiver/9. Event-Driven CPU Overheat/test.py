import unittest

from submission import simulateOverheatController


class TestSimulateOverheatController(unittest.TestCase):
    def simulate(
        self,
        pooled_cooling,
        core_ids,
        active_cooling,
        shutdown_temperature,
        operations,
        operation_data,
    ):
        return simulateOverheatController(
            pooled_cooling,
            core_ids,
            active_cooling,
            shutdown_temperature,
            operations,
            operation_data,
        )

    def test_example_1(self):
        self.assertEqual(
            self.simulate(
                pooled_cooling=4,
                core_ids=[10, 20],
                active_cooling=[1, 1],
                shutdown_temperature=10,
                operations=["SetCoreLoad", "SetCoreLoad", "Tick", "Tick"],
                operation_data=[[0, 10, 8], [0, 20, 4], [2], [3]],
            ),
            [[10], []],
        )

    def test_example_2(self):
        self.assertEqual(
            self.simulate(
                pooled_cooling=3,
                core_ids=[1],
                active_cooling=[2],
                shutdown_temperature=5,
                operations=[
                    "SetCoreLoad",
                    "Tick",
                    "SetCoreLoad",
                    "Tick",
                    "SetCoreLoad",
                    "Tick",
                    "SetCoreLoad",
                    "Tick",
                ],
                operation_data=[
                    [0, 1, 6],
                    [1],
                    [1, 1, 0],
                    [3],
                    [3, 1, 10],
                    [4],
                    [4, 1, 4],
                    [5],
                ],
            ),
            [[], [], [1], [1]],
        )

    def test_initial_tick_has_no_changes(self):
        self.assertEqual(
            self.simulate(10, [7, 8], [1, 2], 10, ["Tick"], [[0]]),
            [[]],
        )

    def test_first_load_change_may_occur_after_time_zero(self):
        self.assertEqual(
            self.simulate(
                pooled_cooling=10,
                core_ids=[1],
                active_cooling=[2],
                shutdown_temperature=100,
                operations=["SetCoreLoad", "Tick"],
                operation_data=[[5, 1, 20], [6]],
            ),
            [[]],
        )

    def test_shutdown_occurs_at_exact_threshold(self):
        self.assertEqual(
            self.simulate(
                0,
                [5],
                [0],
                10,
                ["SetCoreLoad", "Tick", "Tick"],
                [[0, 5, 5], [1], [2]],
            ),
            [[], [5]],
        )

    def test_two_load_changes_at_same_timestamp_use_the_last_load(self):
        self.assertEqual(
            self.simulate(
                0,
                [1],
                [0],
                10,
                ["SetCoreLoad", "SetCoreLoad", "Tick"],
                [[0, 1, 10], [0, 1, 0], [100]],
            ),
            [[]],
        )

    def test_load_update_preserves_temperature_of_running_core(self):
        self.assertEqual(
            self.simulate(
                0,
                [1],
                [0],
                10,
                ["SetCoreLoad", "SetCoreLoad", "Tick", "Tick"],
                [[0, 1, 4], [2, 1, 2], [2], [3]],
            ),
            [[], [1]],
        )

    def test_temperature_can_cool_but_not_below_zero(self):
        self.assertEqual(
            self.simulate(
                0,
                [1],
                [2],
                10,
                [
                    "SetCoreLoad",
                    "SetCoreLoad",
                    "Tick",
                    "SetCoreLoad",
                    "Tick",
                    "Tick",
                ],
                [[0, 1, 8], [1, 1, 0], [3], [3, 1, 6], [4], [5]],
            ),
            [[], [], [1]],
        )

    def test_set_core_load_restarts_and_resets_temperature(self):
        self.assertEqual(
            self.simulate(
                0,
                [1],
                [0],
                5,
                ["SetCoreLoad", "Tick", "SetCoreLoad", "Tick", "Tick"],
                [[0, 1, 5], [1], [1, 1, 0], [1], [2]],
            ),
            [[1], [1], []],
        )

    def test_shutdown_and_restart_before_tick_report_id_once(self):
        self.assertEqual(
            self.simulate(
                0,
                [9],
                [0],
                5,
                ["SetCoreLoad", "SetCoreLoad", "Tick"],
                [[0, 9, 5], [1, 9, 0], [1]],
            ),
            [[9]],
        )

    def test_pooled_cooling_is_redistributed_after_shutdown(self):
        self.assertEqual(
            self.simulate(
                4,
                [1, 2],
                [0, 0],
                10,
                ["SetCoreLoad", "SetCoreLoad", "Tick", "Tick"],
                [[0, 1, 6], [0, 2, 5], [3], [4]],
            ),
            [[1], [2]],
        )

    def test_pooled_cooling_uses_floor_division(self):
        self.assertEqual(
            self.simulate(
                5,
                [1, 2],
                [0, 0],
                2,
                ["SetCoreLoad", "SetCoreLoad", "Tick", "Tick"],
                [[0, 1, 3], [0, 2, 3], [1], [2]],
            ),
            [[], [1, 2]],
        )

    def test_simultaneous_changes_are_sorted_by_numeric_core_id(self):
        self.assertEqual(
            self.simulate(
                0,
                [20, 3, 11],
                [0, 0, 0],
                10,
                ["SetCoreLoad", "SetCoreLoad", "SetCoreLoad", "Tick"],
                [[0, 20, 10], [0, 3, 10], [0, 11, 10], [1]],
            ),
            [[3, 11, 20]],
        )

    def test_tick_clears_the_changed_id_set(self):
        self.assertEqual(
            self.simulate(
                0,
                [1],
                [0],
                1,
                ["SetCoreLoad", "Tick", "Tick", "Tick"],
                [[0, 1, 1], [1], [1], [10]],
            ),
            [[1], [], []],
        )

    def test_extreme_gap_with_intermediate_cooling_redistribution(self):
        self.assertEqual(
            self.simulate(
                pooled_cooling=2,
                core_ids=[1, 2],
                active_cooling=[0, 0],
                shutdown_temperature=1_000_000_000,
                operations=["SetCoreLoad", "SetCoreLoad", "Tick"],
                operation_data=[
                    [0, 1, 3],
                    [0, 2, 2],
                    [1_000_000_000],
                ],
            ),
            [[1]],
        )

    def test_large_timestamp_gap_does_not_require_second_by_second_work(self):
        self.assertEqual(
            self.simulate(
                0,
                [42],
                [0],
                1_000_000_000,
                ["SetCoreLoad", "Tick", "Tick"],
                [[0, 42, 1], [999_999_999], [1_000_000_000]],
            ),
            [[], [42]],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2, failfast=True)
