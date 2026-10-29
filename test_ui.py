"""Headless regression tests for input and the boundary between UI and story."""

import os
import unittest
from collections import defaultdict
from unittest.mock import patch

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from main import Game


class InputTests(unittest.TestCase):
    """Use SDL's dummy driver so tests do not create a desktop game window."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.environment = patch.dict(os.environ, {"SDL_VIDEODRIVER": "dummy"})
        cls.environment.start()
        pygame.display.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()
        cls.environment.stop()

    def setUp(self) -> None:
        self.game = Game(pygame.display.set_mode((1200, 820)))
        self.game.start()

    def press(self, key: int) -> None:
        """Send a key through the same handler used by the game loop."""
        self.game.handle(pygame.event.Event(pygame.KEYDOWN, key=key))

    def test_results_block_new_decisions_until_acknowledged(self) -> None:
        self.press(pygame.K_1)
        self.assertIn("Flashlight", self.game.state.inventory)
        self.press(pygame.K_2)
        self.assertEqual(self.game.state.actions_taken, 1)
        self.press(pygame.K_RETURN)
        self.press(pygame.K_2)
        self.assertEqual(self.game.state.actions_taken, 2)

    def test_scene_change_waits_for_acknowledgement(self) -> None:
        self.press(pygame.K_4)
        self.assertEqual(self.game.state.scene, "road")
        self.assertEqual(self.game.state.pending_scene, "hall")
        self.press(pygame.K_RETURN)
        self.assertEqual(self.game.state.scene, "hall")
        self.assertEqual(self.game.state.decisions, 2)

    def test_pause_and_journal_block_decisions(self) -> None:
        for key in (pygame.K_p, pygame.K_j):
            with self.subTest(key=key):
                self.press(key)
                self.press(pygame.K_1)
                self.assertEqual(self.game.state.actions_taken, 0)
                self.press(key)

    def test_interact_uses_the_nearest_unused_marker(self) -> None:
        self.game.player.update(245, 235)
        self.press(pygame.K_e)
        self.assertIn("Flashlight", self.game.state.inventory)
        self.press(pygame.K_RETURN)
        self.assertIsNone(self.game.nearest())

    def test_diagonal_movement_has_the_same_speed_as_straight_movement(self) -> None:
        start = self.game.player.copy()
        keys = defaultdict(int, {pygame.K_w: 1, pygame.K_d: 1})
        with patch("pygame.key.get_pressed", return_value=keys):
            self.game.update(0.05)
        self.assertAlmostEqual(self.game.player.distance_to(start), 190 * 0.05)

    def test_movement_cannot_cross_solid_furniture(self) -> None:
        self.game.player.update(245, 240)
        start = self.game.player.copy()
        with patch("pygame.key.get_pressed", return_value=defaultdict(int, {pygame.K_s: 1})):
            self.game.update(0.1)
        self.assertEqual(self.game.player, start)

    def test_window_resize_preserves_mouse_hit_coordinates(self) -> None:
        # A half-sized canvas in a 700x410 window has 50-pixel side borders.
        self.game.screen = pygame.display.set_mode((700, 410))
        self.assertEqual(self.game.mouse((350, 205)), (600, 410))
        self.game.draw()
        # Logical point (200, 647) is the first action button.
        self.game.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 323.5)))
        self.assertIn("Flashlight", self.game.state.inventory)

    def test_result_dismissal_without_modal_is_a_no_op(self) -> None:
        self.game.continue_result()
        self.assertEqual(self.game.mode, "play")
        self.assertEqual(self.game.state.scene, "road")


if __name__ == "__main__":
    unittest.main()
