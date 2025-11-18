from libs.actor import Actor, Arena, Point
from actors.zombie import Zombie
from actors.gravestone import Gravestone
from libs.animation import Animation

class Torch(Actor):
    def __init__(self, pos, direction, arena=None):
        self._x, self._y = pos
        self._dir = direction

        # Carica settings se disponibili
        if arena is None:
            # Valori di default
            frames = [((19, 400), (14, 14)), ((39, 400), (14, 14)), ((58, 400), (14, 14)), ((77, 400), (14, 14))]
            speed = 4
            self._speed_x = 4
            self._speed_y_initial = -3
            self._gravity = 0.3
            self._ground_y = 180
        else:
            settings = arena.get_settings()
            torch_config = settings.get_actor_config('torch')

            # Animazione
            anim_data = settings.get_animation_data('torch', 'flying')
            frames = anim_data['frames']
            speed = anim_data['speed']

            # Parametri fisici
            self._speed_x = torch_config['speed_x']
            self._speed_y_initial = torch_config['speed_y_initial']
            self._gravity = torch_config['gravity']
            self._ground_y = torch_config['ground_y']

        self._anim = Animation(frames, speed=speed)
        self._sprite, self._size = self._anim.start()

        self._dx = self._speed_x if self._dir == "right" else -self._speed_x
        self._dy = self._speed_y_initial

    def move(self, arena: Arena):
        self._x += self._dx
        self._y += self._dy

        self._dy += self._gravity
        self._sprite, self._size = self._anim.update()

        for other in arena.collisions():
            if isinstance(other, Zombie):
                arena.kill(other)
                arena.kill(self)
            if isinstance(other, Gravestone):
                arena.spawn(Particle(other.pos(), arena))
                arena.kill(self)
                other.hit()

        if self._y >= self._ground_y:
            arena.spawn(Flame(self.pos(), arena))
            arena.kill(self)

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite


class Flame(Actor):
    def __init__(self, pos, arena=None):
        self._x, self._y = pos

        # Carica settings se disponibili
        if arena is None:
            # Valori di default
            frames = [((117, 428), (32, 32)), ((153, 435), (24, 24)), ((210, 443), (16, 16)), ((229, 450), (8, 8))]
            speed = 15
            self._cooldown = 60
            self._move_down_speed = 8
        else:
            settings = arena.get_settings()
            flame_config = settings.get_actor_config('flame')

            # Animazione
            anim_data = settings.get_animation_data('flame', 'burn')
            frames = anim_data['frames']
            speed = anim_data['speed']

            # Parametri
            self._cooldown = flame_config['cooldown']
            self._move_down_speed = flame_config['move_down_speed']

        self._anim = Animation(frames, speed=speed, loop=True, on_update=self.move_down)
        self._sprite, self._size = self._anim.start()

    def move(self, arena: Arena):
        self._cooldown -= 1
        if self._cooldown == 0:
            self._anim.stop()
            arena.kill(self)
            return

        self._sprite, self._size = self._anim.update()

        for other in arena.collisions():
            if isinstance(other, Zombie):
                arena.kill(other)

    def move_down(self):
        self._y += self._move_down_speed

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite


class Particle(Actor):
    def __init__(self, pos, arena=None):
        self._x, self._y = pos

        # Carica settings se disponibili
        if arena is None:
            # Valori di default
            frames = [((146, 359), (9, 9)), ((157, 358), (11, 11)), ((170, 356), (15, 15))]
            speed = 5
            self._cooldown = 15
        else:
            settings = arena.get_settings()
            particle_config = settings.get_actor_config('particle')

            # Animazione
            anim_data = settings.get_animation_data('particle', 'explode')
            frames = anim_data['frames']
            speed = anim_data['speed']

            # Parametri
            self._cooldown = particle_config['cooldown']

        self._anim = Animation(frames, speed=speed, loop=False)
        self._sprite, self._size = self._anim.start()

    def move(self, arena: Arena):
        self._cooldown -= 1
        if self._cooldown == 0:
            arena.kill(self)
            return
        self._sprite, self._size = self._anim.update()

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
