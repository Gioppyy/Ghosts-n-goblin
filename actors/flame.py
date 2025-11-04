from libs.actor import Actor, Arena, Point
from actors.zombie import Zombie

FRAMES = [
    ((117, 428), (32, 32)),
    ((153, 435), (24, 24)),
    ((210, 443), (16, 16)),
    ((229, 450), (8, 8))
]

class Flame(Actor):
    def __init__(self, pos):
        self._x, self._y = pos
        self._sprite, self._size = FRAMES[0]

        self._prev_idx = 0
        self._cooldown = 60

    def move(self, arena: Arena):
        self._cooldown -= 1
        if self._cooldown == 0:
            arena.kill(self)
            return

        # 15 = durata di ogni frame
        idx = (60 - self._cooldown) // 15 % len(FRAMES)
        if idx != self._prev_idx:
            self._prev_idx = idx
            self._sprite, self._size = FRAMES[idx]
            self._y += 8

        for other in arena.collisions():
            if isinstance(other, Zombie):
                arena.kill(other)

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
