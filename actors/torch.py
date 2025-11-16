from libs.actor import Actor, Arena, Point
from actors.zombie import Zombie
from actors.gravestone import Platform
from libs.animation import Animation

GROUND_Y = 170

class Torch(Actor):
    def __init__(self, pos, direction):
        self._x, self._y = pos

        self._anim = Animation([((19, 400), (14, 14)), ((39, 400), (14, 14)), ((58, 400), (14, 14)), ((77, 400), (14, 14))], speed=4)
        self._sprite, self._size = self._anim.start()

        self._dir = direction
        self._dx = 4 if self._dir == "right" else -4
        self._dy = -3

    def move(self, arena: Arena):
        self._x += self._dx
        self._y += self._dy

        self._dy += 0.3
        self._sprite, self._size = self._anim.update()

        for other in arena.collisions():
            if isinstance(other, Zombie):
                arena.kill(other)
                arena.kill(self)

        if self._y >= GROUND_Y:
            arena.spawn(Flame(self.pos()))
            arena.kill(self)

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite

class Flame(Actor):
    def __init__(self, pos):
        self._x, self._y = pos

        self._anim = Animation([((117, 428), (32, 32)), ((153, 435), (24, 24)), ((210, 443), (16, 16)),((229, 450), (8, 8))], speed=15, loop=True, on_update=self.move_down)

        self._sprite, self._size = self._anim.start()
        self._cooldown = 60

    def move(self, arena: Arena):
        self._cooldown -= 1
        if self._cooldown == 0:
            arena.kill(self)
            return

        self._sprite, self._size = self._anim.update()

        for other in arena.collisions():
            if isinstance(other, Zombie):
                arena.kill(other)

    def move_down(self):
        self._y += 8

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
