import unittest
from actors.arthur import Arthur
from main import GngGame
from actors.zombie import Zombie
from actors.gravestone import Gravestone
import libs.g2d as g2d

class ArthurTest(unittest.TestCase):

    def setUp(self):
        g2d.init_canvas((1, 1))
        self.game = GngGame()
        self.arena = self.game
        self.arthur = Arthur((100, 170), self.arena)

    def test_move_right(self):
        self.arena.current_keys = lambda: ["d"]
        old_x = self.arthur.pos()[0]
        self.arthur.move(self.arena)
        self.assertGreater(self.arthur.pos()[0], old_x)
        self.assertEqual(self.arthur._facing, "right")

    def test_move_left(self):
        self.arena.current_keys = lambda: ["a"]
        old_x = self.arthur.pos()[0]
        self.arthur.move(self.arena)
        self.assertLess(self.arthur.pos()[0], old_x)
        self.assertEqual(self.arthur._facing, "left")

    def test_jump(self):
        self.arena.current_keys = lambda: ["w"]
        self.arena.count = lambda: 0
        old_y = self.arthur.pos()[1]
        self.arthur.move(self.arena)
        self.assertTrue(self.arthur._jumping)
        self.assertLess(self.arthur.pos()[1], old_y)

    def test_gravity(self):
        a = Arthur((100, 50), self.arena)
        old_y = a.pos()[1]
        a.move(self.arena)
        self.assertGreater(a.pos()[1], old_y)

    def test_collision_with_zombie(self):
        zombie = Zombie((self.arthur.pos()[0], self.arthur.pos()[1]), 0, self.arena)
        self.arena.spawn(zombie)
        old_lives = self.arena.get_lives()
        self.arthur.move(self.arena)
        self.assertLess(self.arena.get_lives(), old_lives)

    def test_collision_with_gravestone(self):
        gravestone = Gravestone((self.arthur.pos()[0] + 10, self.arthur.pos()[1]))
        self.arena.spawn(gravestone)
        self.arena.current_keys = lambda: ["d"]
        self.arthur.move(self.arena)
        self.assertLessEqual(self.arthur.pos()[0], gravestone.pos()[0] - self.arthur.size()[0])

    def test_throw_torch(self):
        self.arena.current_keys = lambda: ["f"]
        self.arena.count = lambda: 0
        self.arthur._torch = False
        self.arthur._torch_in_cooldown = False
        torches_before = len([a for a in self.arena.actors() if a.__class__.__name__ == "Torch"])
        self.arthur.move(self.arena)
        torches_after = len([a for a in self.arena.actors() if a.__class__.__name__ == "Torch"])
        self.assertGreater(torches_after, torches_before)
        self.assertTrue(self.arthur._torch)

if __name__ == "__main__":
    unittest.main()
