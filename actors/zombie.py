from libs.actor import Actor, Arena, Point
from random import randint

# ( (sprite_coord), (sprite_size) )
RIGHT = ((654, 66), (21, 31))
LEFT = ((630, 66), (20, 31))
directions = [LEFT, RIGHT]

class Zombie(Actor):
    def __init__(self, pos, direction):
        self._x, self._y = pos

        self._distance = randint(150, 300)
        self._dir = direction
        self._sprite, self._size = directions[self._dir]
        self._dx = 3 if self._dir == 1 else -3

    def move(self, arena: Arena):
        aw, _ = arena.size()

        self._x += self._dx
        self._distance -= self._dx

        if self._x <= 0 or self._distance <= 0:
            arena.kill(self)

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
