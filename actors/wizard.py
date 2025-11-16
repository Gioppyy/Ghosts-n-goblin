from libs.actor import Actor, Point, Arena
from libs.animation import Animation

class Wizard(Actor):
    def __init__(self, pos):
        self._x, self._y = pos

        self._anim = Animation([((544, 900), (20, 33)), ((584, 900), (19, 33)), ((615, 900), (37, 33)),((654, 900), (35, 33))], speed=15, loop=True)

        self._sprite, self._size = self._anim.start()
        self._y -= 15
        self._cooldown = 60

    def move(self, arena: Arena):
        self._cooldown -= 1
        if self._cooldown == 0:
            self._anim.stop()
            arena.kill(self)
            return

        self._sprite, self._size = self._anim.update()

    def pos(self) -> Point:
        return (self._x, self._y)

    def sprite(self) -> Point | None:
        return self._sprite

    def size(self) -> Point:
        return self._size
