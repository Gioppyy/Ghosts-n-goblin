from libs.actor import Actor, Arena, Point
from actors.flame import Flame
from actors.zombie import Zombie

FRAMES = [
    ((19, 400)),
    ((39, 400)),
    ((58, 400)),
    ((77, 400))
]

class Torch(Actor):
    def __init__(self, pos, direction):
        self._x, self._y = pos
        self._sprite = FRAMES[0]

        self._dir = direction
        self._dx = 4 if self._dir == "right" else -4
        self._dy = -3

        self._tick = 0

    def move(self, arena: Arena):
        self._x += self._dx
        self._y += self._dy
        self._dy += 0.3

        for other in arena.collisions():
            if isinstance(other, Zombie):
                arena.kill(other)
                arena.kill(self)

        self._tick += 1

        idx = (self._tick // 4) % len(FRAMES)
        self._sprite = FRAMES[idx]

        # 14 = altezza sprite
        if self._y >= 170:
            arena.spawn(Flame(self.pos()))
            arena.kill(self)


    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return (14, 14)

    def sprite(self) -> Point | None:
        return self._sprite
