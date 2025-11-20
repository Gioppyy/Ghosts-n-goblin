import unittest
from main import GngGame
from actors.torch import Torch, Flame, Particle
from actors.zombie import Zombie
from actors.gravestone import Gravestone
import libs.g2d as g2d

class TorchTest(unittest.TestCase):

    def setUp(self):
        g2d.init_canvas((1, 1))
        self.game = GngGame()
        self.arena = self.game

    def test_torch_falling_and_gravity(self):
        torch = Torch((50, 50), "right", self.arena)
        old_y = torch.pos()[1]
        torch.move(self.arena)
        self.assertGreater(old_y, torch.pos()[1])

    def test_torch_hits_zombie(self):
        torch = Torch((50, 50), "right", self.arena)
        zombie = Zombie((50, 50), 0, self.arena)
        self.arena.spawn(zombie)
        old_score = self.arena.get_score()
        torch.move(self.arena)
        self.assertNotIn(zombie, self.arena.actors())
        self.assertGreater(self.arena.get_score(), old_score)

    def test_torch_hits_gravestone(self):
        torch = Torch((50, 50), "right", self.arena)
        gravestone = Gravestone((50, 50))
        self.arena.spawn(gravestone)
        torch.move(self.arena)
        self.assertNotIn(torch, self.arena.actors())

    def test_flame_moves_down(self):
        flame = Flame((100, 50), self.arena)
        old_y = flame.pos()[1]
        flame.move(self.arena)
        self.assertGreater(flame.pos()[1], old_y)

    def test_flame_dies_after_cooldown(self):
        flame = Flame((100, 50), self.arena)
        flame._cooldown = 1
        flame.move(self.arena)
        self.assertNotIn(flame, self.arena.actors())

    def test_flame_hits_zombie(self):
        flame = Flame((50, 50), self.arena)
        zombie = Zombie((50, 50), 0, self.arena)
        self.arena.spawn(zombie)

        old_score = self.arena.get_score()
        flame.move(self.arena)
        self.assertNotIn(zombie, self.arena.actors())
        self.assertGreater(self.arena.get_score(), old_score)

if __name__ == "__main__":
    unittest.main()
