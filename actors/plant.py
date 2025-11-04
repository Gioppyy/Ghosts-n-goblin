from libs.actor import Actor, Arena, Point
from random import randint

class Plant(Actor):
    def __init__(self, pos: Point):
        self._x, self._y = pos

    def move(self, arena):
        if randint(0, 200) == 100:
            arena.spawn(Eyeball(self.pos(), "left"))

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return (15, 26)

    def sprite(self) -> Point | None:
        return (563, 214)

# eyeball
class Eyeball(Actor):
    def __init__(self, pos: Point, direction: int):
        self._x, self._y = pos
        self._dir = direction
        self._dx = 3 if self._dir == "right" else -3

    def move(self, arena):
        self._x += self._dx
        if self._x < 0:
            arena.kill(self)

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return (9, 9)

    def sprite(self) -> Point | None:
        return (645, 500)
