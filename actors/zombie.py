from libs.actor import Actor, Arena, Point
from random import randint
from libs.animation import Animation

# ( (sprite_coord), (sprite_size) )
RIGHT = [((654, 66), (21, 31)), ((677, 65), (14, 30)), ((699, 65), (21, 31))]
DEATH_RIGHT = [((725, 73), (19, 23)), ((748, 85), (24, 10)), ((777, 88), (16, 18))]
LEFT = [((630, 66), (20, 31)), ((610, 65), (14,30)), ((585, 67), (21, 31))]
DEATH_LEFT = [((562, 73), (19,23)), ((533, 85), (24,10)), ((512, 88), (16, 18))]

class Zombie(Actor):
    def __init__(self, pos, direction, arena):
        self._x, self._y = pos
        self._dir = direction

        self._distance = randint(150, 300)
        self._dx = 3 if self._dir == 1 else -3

        self._frames = LEFT if self._dir == 0 else RIGHT
        self._death_frames = DEATH_LEFT if self._dir == 0 else DEATH_RIGHT
        self._walk_anim = Animation(self._frames, speed=5)
        self._death_anim = Animation(self._death_frames, speed=5, loop=False, on_update=self.move_down, on_complete=arena.kill(self))

        self._sprite, self._size = self._walk_anim.start()

    def move(self, arena: Arena):
        aw, _ = arena.size()

        if self._walk_anim.is_active():
            self._sprite, self._size = self._walk_anim.update()
        else:
            self._sprite, self._size = self._death_anim.update()

        self._x += self._dx
        self._distance -= self._dx

        if self._x <= 0 or self._distance <= 0 and not self._death_anim.is_active():
            self._death_anim.start()
            self._walk_anim.stop()
            self._dx = 0

    def move_down(self):
        self._y += 6

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
