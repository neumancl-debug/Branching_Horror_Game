"""Regression checks for the prototype's branching rules."""

import unittest

from story import CHARACTERS, SCENES, GameState


def take(state: GameState, *actions: str) -> GameState:
    """Play actions in order, acknowledging each outcome before the next one."""
    for action in actions:
        result = state.choose(action)
        if result is None:
            raise AssertionError(f"Action rejected: {state.scene}/{action}")
        state.enter_pending()
    return state


class StoryTests(unittest.TestCase):
    """Exercise player-visible routes and the decision system's invariants."""

    def test_all_characters_can_escape_with_evidence(self):
        for character in CHARACTERS:
            with self.subTest(character=character):
                state = GameState(character)
                take(
                    state,
                    "glovebox",
                    "tracks",
                    "estate",
                    "note",
                    "chandelier",
                    "pantry",
                    "scratches",
                    "basement",
                    "log",
                    "panel",
                    "passage",
                    "gate",
                )
                self.assertEqual(state.ending, "THE TRUTH GETS OUT")

    def test_all_characters_can_use_the_trap(self):
        for character in CHARACTERS:
            with self.subTest(character=character):
                state = GameState(character)
                take(
                    state,
                    "glovebox",
                    "estate",
                    "chandelier",
                    "dining",
                    "pantry",
                    "basement",
                    "passage",
                    "trap",
                )
                self.assertEqual(state.ending, "THE HOUSE TURNS ON HIM")

    def test_character_specific_routes(self):
        state = GameState("Marcus", scene="dining")
        take(state, "window")
        self.assertEqual(state.ending, "THROUGH THE THORNS")
        state = GameState("Noah", scene="basement")
        take(state, "panel")
        self.assertTrue(state.gate_override_disabled)
        self.assertNotIn("Gate override disabled", state.inventory)
        state = GameState("Sofia", scene="basement")
        take(state, "passage")
        self.assertEqual(state.threat, 0)
        state = GameState("Evelyn")
        take(state, "tracks")
        self.assertIn("rig", state.clues)

    def test_failed_attempt_spends_decision_and_cannot_be_repeated(self):
        state = GameState("Evelyn", scene="basement")
        take(state, "panel")
        self.assertEqual(state.decisions, 2)
        self.assertEqual(state.threat, 2)
        self.assertIsNone(state.choose("panel"))
        self.assertEqual(state.decisions, 2)
        self.assertIsNone(state.choose("made_up"))

    def test_exhaustion_advances_and_resets_scene(self):
        state = GameState("Sofia")
        state.choose("glovebox")
        state.choose("tracks")
        result = state.choose("listen")
        self.assertIn("Time runs out", result)
        self.assertEqual(state.pending_scene, "hall")
        self.assertIsNone(state.choose("estate"))
        state.enter_pending()
        self.assertEqual(state.scene, "hall")
        self.assertEqual(state.decisions, 2)
        self.assertFalse(state.used)

    def test_stairs_warning_changes_outcome(self):
        state = GameState("Marcus", scene="hall", decisions=2)
        take(state, "stairs")
        self.assertEqual(state.ending, "THE STAIRCASE")
        state = GameState("Marcus", scene="hall", decisions=2)
        take(state, "note", "stairs")
        self.assertIsNone(state.ending)
        self.assertEqual(state.scene, "dining")

    def test_fatal_choices_and_threat_limit(self):
        for scene, action in (("basement", "switch"), ("yard", "fight"), ("yard", "trap")):
            state = GameState("Evelyn", scene=scene, decisions=SCENES[scene].decisions)
            take(state, action)
            self.assertIsNotNone(state.ending)
            self.assertIsNone(state.choose(action))
        state = GameState("Evelyn", scene="dining", threat=4)
        take(state, "window")
        self.assertEqual(state.ending, "FOUND IN THE DARK")

    def test_last_yard_decision_requires_a_resolution(self):
        state = GameState("Evelyn", scene="yard", decisions=2)
        take(state, "hide", "gate")
        self.assertEqual(state.ending, "NOWHERE LEFT TO HIDE")

    def test_plain_escape_and_pending_transition_death(self):
        state = GameState("Marcus", scene="yard", decisions=2)
        take(state, "gate")
        self.assertEqual(state.ending, "OUT OF BLACKTHORN")
        state = GameState("Evelyn", scene="basement", threat=5)
        take(state, "passage")
        self.assertEqual(state.ending, "FOUND IN THE DARK")
        self.assertIsNone(state.pending_scene)

    def test_exhaustion_can_raise_threat_to_six(self):
        state = GameState("Sofia", threat=5, decisions=1)
        take(state, "glovebox")
        self.assertEqual(state.threat, 6)
        self.assertEqual(state.ending, "FOUND IN THE DARK")
        self.assertIsNone(state.pending_scene)

    def test_history_includes_the_entire_displayed_result(self):
        state = GameState("Sofia", decisions=1)
        message = state.choose("glovebox")
        self.assertIn("Time runs out", message)
        self.assertEqual(state.history[-1], message)

    def test_zero_decisions_rejects_actions_without_mutating_state(self):
        state = GameState("Evelyn", decisions=0)
        self.assertIsNone(state.choose("glovebox"))
        self.assertEqual(state.actions_taken, 0)
        self.assertFalse(state.inventory)
        self.assertFalse(state.used)

    def test_scene_budget_defaults_to_selected_scene(self):
        self.assertEqual(GameState("Evelyn", scene="hall").decisions, 2)
        self.assertEqual(GameState("Evelyn", scene="yard").decisions, 2)

    def test_invalid_starting_data_is_rejected(self):
        for arguments in (
            {"character": "Nobody"},
            {"character": "Evelyn", "scene": "missing"},
            {"character": "Evelyn", "decisions": -1},
            {"character": "Evelyn", "threat": -1},
        ):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                GameState(**arguments)

    def test_separate_runs_do_not_share_mutable_containers(self):
        first = GameState("Evelyn")
        second = GameState("Evelyn")
        take(first, "glovebox", "tracks")
        self.assertFalse(second.inventory)
        self.assertFalse(second.clues)
        self.assertFalse(second.used)
        self.assertFalse(second.history)

    def test_override_alone_can_unlock_the_gate(self):
        state = GameState("Noah", scene="basement")
        take(state, "panel", "passage", "gate")
        self.assertTrue(state.survived)
        self.assertEqual(state.ending, "OUT OF BLACKTHORN")


if __name__ == "__main__":
    unittest.main()
