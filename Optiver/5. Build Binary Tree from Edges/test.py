import unittest
from contextlib import redirect_stdout
from io import StringIO

from submission import buildSExpression


class DetailedTestResult(unittest.TextTestResult):
    """Show the input responsible for a failure and a concise pass count."""

    def _show_input(self, test):
        pairs = getattr(test, "current_input", "<input not recorded>")
        self.stream.writeln(f"Failing input: {pairs!r}")
        debug_output = getattr(test, "debug_output", "").strip()
        if debug_output:
            self.stream.writeln(f"Captured debug output:\n{debug_output}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._show_input(test)

    def addError(self, test, err):
        super().addError(test, err)
        self._show_input(test)

    def stopTestRun(self):
        super().stopTestRun()
        skipped = len(self.skipped)
        passed = self.testsRun - len(self.failures) - len(self.errors) - skipped
        self.stream.writeln(
            f"Passed: {passed}/{self.testsRun} "
            f"(failed: {len(self.failures)}, errors: {len(self.errors)}, "
            f"skipped: {skipped})"
        )


class BuildSExpressionTests(unittest.TestCase):
    def run_build(self, pairs):
        self.current_input = pairs
        output = StringIO()
        try:
            with redirect_stdout(output):
                return buildSExpression(pairs)
        finally:
            self.debug_output = output.getvalue()

    def assert_result(self, pairs, expected):
        actual = self.run_build(pairs)
        self.assertIsInstance(actual, str)
        self.assertEqual(actual, expected)

    # Valid trees and S-expression ordering

    def test_given_valid_example(self):
        self.assert_result(
            ["(A,B)", "(B,C)", "(A,D)"],
            "(A(B(C))(D))",
        )

    def test_single_edge(self):
        self.assert_result(["(A,B)"], "(A(B))")

    def test_parent_letter_can_be_greater_than_child(self):
        self.assert_result(["(Z,A)"], "(Z(A))")

    def test_children_are_sorted_lexicographically(self):
        self.assert_result(["(A,D)", "(A,B)"], "(A(B)(D))")

    def test_pair_order_does_not_change_output(self):
        expected = "(M(B(A)(C))(Z(Y)))"
        cases = [
            ["(M,Z)", "(B,C)", "(Z,Y)", "(M,B)", "(B,A)"],
            ["(B,A)", "(M,B)", "(Z,Y)", "(B,C)", "(M,Z)"],
        ]
        for pairs in cases:
            with self.subTest(pairs=pairs):
                self.assert_result(pairs, expected)

    def test_unbalanced_tree(self):
        self.assert_result(
            ["(D,B)", "(B,A)", "(D,F)", "(F,E)", "(F,G)"],
            "(D(B(A))(F(E)(G)))",
        )

    # E1: malformed input

    def test_empty_input_is_e1(self):
        self.assert_result([], "E1")

    def test_malformed_pair_variations_are_e1(self):
        malformed = [
            "A,B",
            "(A, B)",
            "(A,B)extra",
            "(AA,B)",
            "(A,BB)",
            "(a,B)",
            "(A,b)",
            "[A,B]",
            "(A-B)",
            "(A;B)",
            "(A,B",
            "A,B)",
            "",
            "     ",
        ]
        for bad_pair in malformed:
            with self.subTest(bad_pair=bad_pair):
                self.assert_result([bad_pair], "E1")

    def test_e1_has_priority_even_when_malformed_pair_is_last(self):
        self.assert_result(["(A,B)", "(A,B)", "A,C"], "E1")

    # E2: duplicate directed pair

    def test_duplicate_pair_is_e2(self):
        self.assert_result(["(A,B)", "(A,B)"], "E2")

    def test_reverse_pair_is_not_a_duplicate(self):
        self.assert_result(["(A,B)", "(B,A)"], "E5")

    def test_e2_has_priority_over_e3_even_when_duplicate_is_last(self):
        self.assert_result(
            ["(A,B)", "(A,C)", "(A,D)", "(A,B)"],
            "E2",
        )

    def test_e2_has_priority_over_cycle(self):
        self.assert_result(["(A,B)", "(B,A)", "(A,B)"], "E2")

    # E3: more than two distinct children

    def test_three_children_is_e3(self):
        self.assert_result(["(A,B)", "(A,C)", "(A,D)"], "E3")

    def test_third_child_detected_when_edges_are_separated(self):
        self.assert_result(
            ["(A,Z)", "(B,C)", "(A,M)", "(C,D)", "(A,B)"],
            "E3",
        )

    def test_e3_has_priority_over_multiple_roots(self):
        self.assert_result(
            ["(A,B)", "(A,C)", "(A,D)", "(X,Y)"],
            "E3",
        )

    # E4: multiple roots or multiple parents

    def test_two_separate_trees_is_e4(self):
        self.assert_result(["(A,B)", "(C,D)"], "E4")

    def test_child_with_two_parents_is_e4(self):
        self.assert_result(["(A,B)", "(C,B)"], "E4")

    def test_diamond_has_one_root_but_multiple_parents(self):
        self.assert_result(
            ["(A,B)", "(A,C)", "(B,D)", "(C,D)"],
            "E4",
        )

    def test_e4_has_priority_over_cycle(self):
        self.assert_result(["(A,B)", "(B,D)", "(D,B)"], "E4")

    def test_many_separate_components_is_e4(self):
        self.assert_result(
            ["(A,B)", "(C,D)", "(E,F)", "(G,H)", "(I,J)"],
            "E4",
        )

    # E5: cycles

    def test_self_cycle_is_e5(self):
        self.assert_result(["(A,A)"], "E5")

    def test_two_node_cycle_is_e5(self):
        self.assert_result(["(A,B)", "(B,A)"], "E5")

    def test_long_cycle_is_e5(self):
        self.assert_result(
            ["(A,B)", "(B,C)", "(C,D)", "(D,E)", "(E,A)"],
            "E5",
        )

    def test_disconnected_cycle_hidden_from_apparent_root_is_e5(self):
        self.assert_result(
            ["(A,B)", "(C,D)", "(D,E)", "(E,C)"],
            "E5",
        )

    # Extreme A-Z cases

    def test_extreme_26_node_chain(self):
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        pairs = [f"({letters[i]},{letters[i + 1]})" for i in range(25)]
        expected = "".join(f"({letter}" for letter in letters) + ")" * 26
        self.assert_result(pairs, expected)

    def test_extreme_26_node_balanced_tree_in_reverse_input_order(self):
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        edges = [
            (letters[(index - 1) // 2], letters[index])
            for index in range(1, 26)
        ]
        children = {letter: [] for letter in letters}
        for parent, child in edges:
            children[parent].append(child)

        def expression(node):
            return "(" + node + "".join(
                expression(child) for child in sorted(children[node])
            ) + ")"

        pairs = [f"({parent},{child})" for parent, child in reversed(edges)]
        self.assert_result(pairs, expression("A"))

    def test_extreme_cycle_uses_all_26_nodes(self):
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        pairs = [f"({letters[i]},{letters[(i + 1) % 26]})" for i in range(26)]
        self.assert_result(pairs, "E5")

    def test_extreme_two_large_components_is_e4(self):
        first = "ABCDEFGHIJKLM"
        second = "NOPQRSTUVWXYZ"
        pairs = [f"({group[i]},{group[i + 1]})"
                 for group in (first, second)
                 for i in range(len(group) - 1)]
        self.assert_result(pairs, "E4")


if __name__ == "__main__":
    unittest.main(
        verbosity=2,
        failfast=True,
        testRunner=unittest.TextTestRunner(
            verbosity=2,
            failfast=True,
            resultclass=DetailedTestResult,
        ),
    )
