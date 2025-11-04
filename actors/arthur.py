from libs.actor import Actor, Arena, Point
from actors.zombie import Zombie
from actors.torch import Torch
from actors.gravestone import Gravestone
from actors.plant import Eyeball

# ( (sprite_coord), (sprite_size) )
DEFAULT = ((6, 43), (20, 31))
LEFT_DEFAULT = ((486, 43), (20, 31))
JUMP_RIGHT = ((144, 29), (32, 27))
JUMP_LEFT = ((336, 29), (32, 27))

class Arthur(Actor):
    def __init__(self, pos):
        self._x, self._y = pos
        self._dx, self._dy = 5, 15
        self._sprite, self._size = DEFAULT # fermo
        self._facing = "right"

        self._torch_cooldown = 0 # cooldown per la torcia

        # variabili per il salto
        self._animation = False
        self._animation_tick = 0
        self._animation_cooldown = 0

        # variabili per la camminata
        self._walk_right = [((40, 40), (25, 30)), ((65, 40), (20, 30)), ((85, 40), (23, 30)), ((108, 40), (25, 30))]
        self._walk_left = [((448, 40), (25, 31)), ((425, 40), (23, 31)), ((403, 40), (20, 31)), ((375, 40), (25, 31))]

        self._walk_frame = 0
        self._walk_tick = 0
        self._walk_speed = 5  # ogni 5 tick cambia frame

    def move(self, arena: Arena):
        aw, _ = arena.size()
        keys = arena.current_keys()

        if self._torch_cooldown > 0:
            self._torch_cooldown -= 1

        if self._animation_tick > 0: # arthur sta saltando
            self._animation_tick -= 1
            if self._animation_tick == 0:
                self._animation = False
                self._sprite, self._size = (
                    DEFAULT if self._facing == "right" else LEFT_DEFAULT
                )
                self._y += self._dy
                self._animation_cooldown = 30

        if self._animation_cooldown > 0:
            self._animation_cooldown -= 1

        old_x, old_y = self._x, self._y

        if "f" in keys and self._torch_cooldown == 0: # lancia torcia
            arena.spawn(Torch(self.pos(), self._facing))
            self._torch_cooldown = 10

        if "d" in keys: # cammina a dx
            self._x = min((self._x + self._dx), aw)
            self._facing = "right"
            if not self._animation:
                self.update_walk_animation(self._walk_right)
            else:
                self._sprite, self._size = JUMP_RIGHT

        elif "a" in keys: # cammina a sx
            self._x = max(0, (self._x - self._dx))
            self._facing = "left"
            if not self._animation:
                self.update_walk_animation(self._walk_left)
            else:
                self._sprite, self._size = JUMP_LEFT

        else:
            if not self._animation:
                self._sprite, self._size = (
                    DEFAULT if self._facing == "right" else LEFT_DEFAULT
                )
                self._walk_frame = 0
                self._walk_tick = 0

        if "w" in keys: # salto
            if not self._animation and not self._animation_cooldown > 0:
                self._y -= self._dy
                self._animation = True
                self._animation_tick = 10
                self._sprite, self._size = (
                    JUMP_RIGHT if self._facing == "right" else JUMP_LEFT
                )

        for obj in arena.collisions():
            if isinstance(obj, Zombie) or isinstance(obj, Eyeball):
                arena.decrease_lives()
                arena.kill(obj)
                if arena.get_lives() == 0:
                    arena.kill(self)
                    arena.set_status(False, "Monster")

            if isinstance(obj, Gravestone):
                obj_x, obj_y = obj.pos()
                obj_w, obj_h = obj.size()
                arthur_w, arthur_h = self._size

                if (self._x < obj_x + obj_w and self._x + arthur_w > obj_x and self._y < obj_y + obj_h and self._y + arthur_h > obj_y):
                    if self._x > old_x: # si muove a dx, lo blocco
                        self._x = obj_x - arthur_w
                    elif self._x < old_x: # idem a sx
                        self._x = obj_x + obj_w
                    elif self._y > old_y: # quando salta
                        self._y = obj_y - arthur_h
                    elif self._y < old_y:
                        self._y = obj_y + obj_h

    def update_walk_animation(self, frames):
        self._walk_tick += 1
        if self._walk_tick >= self._walk_speed:
            self._walk_tick = 0
            self._walk_frame = (self._walk_frame + 1) % len(frames)
        self._sprite, self._size = frames[self._walk_frame]

    def facing(self) -> str:
        return self._facing

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
