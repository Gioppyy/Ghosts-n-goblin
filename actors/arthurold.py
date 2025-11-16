from libs.actor import Actor, Arena, Point
from actors.zombie import Zombie
from actors.torch import Torch
from actors.plant import Eyeball
from actors.gravestone import Gravestone, Platform, Ladder
from libs.animation import Animation

DEFAULT = ((5, 45), (20, 30))
LEFT_DEFAULT = ((485, 45), (20, 30))
JUMP_RIGHT = ((144, 29), (32, 27))
JUMP_LEFT = ((336, 29), (32, 27))

class Arthur(Actor):
    def __init__(self, pos):
        self._x, self._y = pos
        self._dx, self._dy = 5, 15
        self._sprite, self._size = DEFAULT # fermo

        self._facing = "right"

        self._torch_cooldown = 0 # cooldown per la torcia

        self._jumping = False

        self._animation = False
        self._animation_tick = 0
        self._animation_cooldown = 0

        # variabili per la camminata
        self._walk_right = Animation(
            [((40,40),(25,30)), ((65,40),(20,30)), ((85,40),(23,30)), ((108,40),(25,30))],
            speed=5, loop=True
        )
        self._walk_left = Animation(
            [((448, 40), (25, 31)), ((425, 40), (23, 31)), ((403, 40), (20, 31)), ((375, 40), (25, 31))],
            speed=5, loop=True
        )

        self._throw_frame = 0
        self._throw_right = [((4, 133), (25, 30)), ((29, 133), (25, 30))]
        self._throw_left = [((483, 133), (25, 30)), ((456, 133), (25, 30))]

        self._walk_frame = 0
        self._walk_tick = 0
        self._walk_speed = 5  # ogni 5 tick cambia frame

        self._on_ladder = False

    def move(self, arena: Arena):
        aw, ah = arena.size()
        keys = arena.current_keys()

        if self._torch_cooldown > 0:
            self._torch_cooldown -= 1

        if self._animation_tick > 0:
            self._animation_tick -= 1

            if self._animation == "throw":
                if self._animation_tick == 4:
                    self._throw_frame = 1
                    frames = self._throw_right if self._facing == "right" else self._throw_left
                    self._sprite, self._size = frames[self._throw_frame]

                if self._animation_tick == 0:
                    self._animation = False
                    self._sprite, self._size = (DEFAULT if self._facing == "right" else LEFT_DEFAULT)
                return

            if self._animation_tick == 0:
                self._animation = False
                self._sprite, self._size = (DEFAULT if self._facing == "right" else LEFT_DEFAULT)
                self._y += self._dy
                self._animation_cooldown = 30

        if self._animation_cooldown > 0:
            self._animation_cooldown -= 1

        old_x, old_y = self._x, self._y


        for obj in arena.collisions():
            if isinstance(obj, Zombie) or isinstance(obj, Eyeball):
                arena.decrease_lives()
                arena.kill(obj)
                if arena.get_lives() == 0:
                    arena.kill(self)
                    arena.set_status(True, "Monster")

            elif isinstance(obj, Gravestone):
                obj_x, obj_y = obj.pos()
                obj_w, obj_h = obj.size()
                arthur_w, arthur_h = self._size

                if (self._x < obj_x + obj_w and self._x + arthur_w > obj_x and
                    self._y < obj_y + obj_h and self._y + arthur_h > obj_y):

                    if self._x > old_x:  # si muove a destra
                        self._x = obj_x - arthur_w
                    elif self._x < old_x:  # si muove a sinistra
                        self._x = obj_x + obj_w
                    elif self._y > old_y:  # atterra sopra
                        self._y = obj_y - arthur_h
                    elif self._y < old_y:  # urta dal basso
                        self._y = obj_y + obj_h

            elif isinstance(obj, Ladder):
                ladder_x, ladder_y = obj.pos()
                ladder_w, ladder_h = obj.size()
                arthur_w, arthur_h = self._size

                x_on_ladder = (self._x + arthur_w > ladder_x) and (self._x < ladder_x + ladder_w)
                y_on_ladder = (self._y + arthur_h > ladder_y) and (self._y < ladder_y + ladder_h)

                if x_on_ladder and y_on_ladder:
                    if not self._on_ladder:
                        self._x = ladder_x + ladder_w//2 - arthur_w//2
                    self._on_ladder = True
                else:
                    if self._on_ladder:
                        self._on_ladder = False
                        self._sprite, self._size = (DEFAULT if self._facing == "right" else LEFT_DEFAULT)

                if self._on_ladder:
                    climb_frames = [((149, 133), (25, 30)), ((339, 133), (25, 30))]
                    top_frames = [((198, 133), (25, 30)), ((222, 133), (25, 30))]
                    climb_speed = 3

                    if "w" in keys:
                        if self._y + arthur_h > ladder_y:
                            self._y -= climb_speed
                            frame = (arena.count() // 10) % 2
                            self._sprite, self._size = climb_frames[frame]
                        else:
                            frame = (arena.count() // 10) % 2
                            self._sprite, self._size = top_frames[frame]

                    elif "s" in keys:
                        if self._y + arthur_h < ladder_y + ladder_h:
                            self._y += climb_speed
                            frame = (arena.count() // 10) % 2
                            self._sprite, self._size = climb_frames[frame]

                    else:
                        self._sprite, self._size = climb_frames[0]

            elif isinstance(obj, Platform):
                obj_x, obj_y = obj.pos()
                obj_w, obj_h = obj.size()
                arthur_w, arthur_h = self._size

                if (self._x < obj_x + obj_w and self._x + arthur_w > obj_x and
                    self._y + arthur_h > obj_y and self._y + arthur_h < obj_y + obj_h):
                    self._y = obj_y - arthur_h

    def update_walk_animation(self, frames):
        self._walk_tick += 1
        if self._walk_tick >= self._walk_speed:
            self._walk_tick = 0
            self._walk_frame = (self._walk_frame + 1) % len(frames)
        self._sprite, self._size = frames[self._walk_frame]

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
