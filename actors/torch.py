from libs.actor import Actor, Arena, Point
from actors.zombie import Zombie

FRAMES = [((19, 400)), ((39, 400)), ((58, 400)), ((77, 400))]

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

FRAMES2 = [((117, 428), (32, 32)), ((153, 435), (24, 24)), ((210, 443), (16, 16)),((229, 450), (8, 8))]

class Flame(Actor):
    def __init__(self, pos):
        self._x, self._y = pos
        self._sprite, self._size = FRAMES2[0]

        self._prev_idx = 0
        self._cooldown = 60

    def move(self, arena: Arena):
        self._cooldown -= 1
        if self._cooldown == 0:
            arena.kill(self)
            return

        # 15 = durata di ogni frame
        idx = (60 - self._cooldown) // 15 % len(FRAMES2)
        if idx != self._prev_idx:
            self._prev_idx = idx
            self._sprite, self._size = FRAMES2[idx]
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
