from libs.actor import Actor, Point
from random import randint, random

class Plant(Actor):
    def __init__(self, pos: Point, arena=None):
        self._x, self._y = pos

        if arena is None:
            self._sprite = (563, 214)
            self._size = (15, 26)
            self._spawn_chance = 200
            self._spawn_target = 100
        else:
            settings = arena.get_settings()
            plant_config = settings.get_actor_config('plant')
            self._sprite = tuple(plant_config['sprite'])
            self._size = tuple(plant_config['size'])
            self._spawn_chance = plant_config['spawn_chance']
            self._spawn_target = plant_config['spawn_target']

    def move(self, arena):
        if randint(0, self._spawn_chance) == self._spawn_target:
            arena.spawn(Eyeball(self.pos(), "left", arena))

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite


# eyeball
class Eyeball(Actor):
    def __init__(self, pos: Point, direction: str, arena=None):
        self._x, self._y = pos
        self._dir = direction

        # Carica settings se disponibili
        if arena is None:
            # Valori di default
            self._speed_x = 3
            self._sprite = (645, 500)
            self._size = (9, 9)
            self._max_y = 200
            speed_y_min = 1
            speed_y_max = 2
        else:
            settings = arena.get_settings()
            eyeball_config = settings.get_actor_config('eyeball')
            self._speed_x = eyeball_config['speed_x']
            self._sprite = tuple(eyeball_config['sprite'])
            self._size = tuple(eyeball_config['size'])
            self._max_y = eyeball_config['max_y']
            speed_y_min = eyeball_config['speed_y_min']
            speed_y_max = eyeball_config['speed_y_max']

        self._dx = self._speed_x if self._dir == "right" else -self._speed_x
        self._dy = random() * (speed_y_max - speed_y_min) + speed_y_min

    def move(self, arena):
        self._x += self._dx
        self._y += self._dy

        if self._x < 0 or self._y >= self._max_y:
            arena.kill(self)

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
