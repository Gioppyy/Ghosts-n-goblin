from libs.actor import Actor, Arena, Point
from libs.animation import Animation

class Princess(Actor):
    def __init__(self, pos: Point, arena=None):
        self._x, self._y = pos
        self._timer = 0
        self._captured = False
        self._alerted = False

        # Carica settings se disponibili
        if arena is None:
            # Valori di default
            frames = [((539, 609), (18, 30)), ((557, 609), (18, 30)), ((575, 609), (18, 30)),
                     ((593, 609), (18, 30)), ((610, 609), (18, 30)), ((627, 609), (25, 30))]
            speed = 15
        else:
            settings = arena.get_settings()
            anim_data = settings.get_animation_data('princess', 'alert')
            frames = anim_data['frames']
            speed = anim_data['speed']

        self._sprite, self._size = frames[0]
        self._anim = Animation(frames, loop=False, speed=speed)
        self._anim.set_on_complete(self._anim.stop)

    def move(self, arena: Arena):
        if self._captured:
            for actor in arena.actors():
                if isinstance(actor, Devil) and actor._phase == "fly":
                    self._x = actor._x
                    self._y = actor._y
            return

        for actor in arena.actors():
            if isinstance(actor, Devil) and actor._phase == "spawn":
                self._alerted = True

        if self._alerted:
            if not self._anim.is_active():
                self._sprite, self._size = self._anim.start()
            else:
                self._sprite, self._size = self._anim.update()

    def capture(self):
        self._captured = True

    def captured(self):
        return self._captured

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite


class Devil(Actor):
    def __init__(self, pos: Point, target: Actor | None = None, arena=None):
        self._x, self._y = pos
        self._target = target
        self._frame = 0
        self._phase = "spawn"
        self._tick = 0

        # Carica settings se disponibili
        if arena is None:
            # Valori di default
            self._spawn_frames = [((531, 302), (42, 32)), ((607, 335), (45, 30))]
            self._fly_frames = [((560, 336), (35, 30)), ((562, 240), (26, 28))]
            self._spawn_speed = 10
            self._spawn_duration = 40
            self._fly_speed = 8
            self._grab_speed = 2
            self._dx, self._dy = 2, -1
            self._fly_exit_y = -50
            self._grab_threshold = 5
        else:
            settings = arena.get_settings()
            devil_config = settings.get_actor_config('devil')

            # Animazioni
            spawn_data = settings.get_animation_data('devil', 'spawn')
            self._spawn_frames = spawn_data['frames']
            self._spawn_speed = spawn_data['speed']
            self._spawn_duration = devil_config['animations']['spawn']['duration']

            fly_data = settings.get_animation_data('devil', 'fly')
            self._fly_frames = fly_data['frames']
            self._fly_speed = fly_data['speed']

            # Velocità
            speed_config = devil_config['speed']
            self._grab_speed = speed_config['grab']
            self._dx = speed_config['fly_x']
            self._dy = speed_config['fly_y']

            # Altri parametri
            self._fly_exit_y = devil_config['fly_exit_y']
            self._grab_threshold = devil_config['grab_threshold']

        self._sprite, self._size = self._spawn_frames[0]

    def move(self, arena: Arena):
        self._tick += 1

        if self._phase == "spawn":
            if self._tick % self._spawn_speed == 0:
                self._frame = (self._frame + 1) % len(self._spawn_frames)
                self._sprite, self._size = self._spawn_frames[self._frame]
            if self._tick > self._spawn_duration:
                self._phase = "grab"
                self._tick = 0

        elif self._phase == "grab":
            if self._target:
                tx, ty = self._target.pos()
                self._x += self._grab_speed if self._x < tx else -self._grab_speed
                self._y += self._grab_speed if self._y < ty else -self._grab_speed

                if abs(self._x - tx) < self._grab_threshold and abs(self._y - ty) < self._grab_threshold:
                    self._target.capture()
                    self._phase = "fly"
                    self._tick = 0
                    self._frame = 0

        elif self._phase == "fly":
            self._x += self._dx
            self._y += self._dy
            if self._tick % self._fly_speed == 0:
                self._frame = (self._frame + 1) % len(self._fly_frames)
                self._sprite, self._size = self._fly_frames[self._frame]

            if self._y < self._fly_exit_y:
                arena.kill(self)

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
