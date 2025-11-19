from libs.actor import Actor, Point, Arena
from libs.animation import Animation

class Wizard(Actor):
    def __init__(self, pos, arena=None):
        self._x, self._y = pos

        if arena is None:
            frames = [((544, 900), (20, 33)), ((584, 900), (19, 33)), ((615, 900), (37, 33)), ((654, 900), (35, 33))]
            speed = 15
            self._cooldown = 60
            offset_y = -15
        else:
            settings = arena.get_settings()
            wizard_config = settings.get_actor_config('wizard')

            anim_data = settings.get_animation_data('wizard', 'cast')
            frames = anim_data['frames']
            speed = anim_data['speed']

            self._cooldown = wizard_config['cooldown']
            offset_y = wizard_config['offset_y']

        self._anim = Animation(frames, speed=speed, loop=True)
        self._sprite, self._size = self._anim.start()
        self._y += offset_y

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
