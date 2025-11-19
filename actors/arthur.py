from libs.actor import Actor, Arena, Point
from actors.zombie import Zombie
from actors.torch import Torch
from actors.plant import Eyeball
from actors.gravestone import Gravestone, Platform, Ladder
from libs.animation import Animation

class Arthur(Actor):
    def __init__(self, pos, arena=None):
        self._x, self._y = pos

        if arena is None:
            self._init_default()
        else:
            self._init_from_settings(arena.get_settings())

        self._facing = "right"
        self._jumping = False
        self._jump_time = 0
        self._jump_cooldown_time = 0
        self._jump_in_cooldown = False

        self._torch = False
        self._torch_time = 0
        self._torch_cooldown_time = 0
        self._torch_in_cooldown = False
        self._throw_animation = None
        self._on_ladder = False

    def _init_default(self):
        self._dx, self._dy = 5, 15
        self._sprite, self._size = ((5, 45), (20, 30))
        self._default_right = ((5, 45), (20, 30))
        self._default_left = ((485, 45), (20, 30))
        self._jump_right = ((144, 29), (32, 27))
        self._jump_left = ((336, 29), (32, 27))
        self._jump_cooldown = 20
        self._jump_duration = 10
        self._torch_cooldown = 15
        self._torch_duration = 10
        self._climb_speed = 3
        self._ladder_exit_height = 120

        self._walk_right = Animation(
            [((40,40),(25,30)), ((65,40),(20,30)), ((85,40),(23,30)), ((108,40),(25,30))],
            speed=5, loop=True
        )
        self._walk_left = Animation(
            [((448, 40), (25, 31)), ((425, 40), (23, 31)), ((403, 40), (20, 31)), ((375, 40), (25, 31))],
            speed=5, loop=True
        )
        self._throw_right = Animation([((4, 133), (25, 30)), ((29, 133), (25, 30))], speed=4)
        self._throw_left = Animation([((483, 133), (25, 30)), ((456, 133), (25, 30))], speed=4)

        climb_frames = [((149, 133), (25, 30)), ((339, 133), (25, 30))]
        top_frames = [((198, 133), (25, 30)), ((222, 133), (25, 30))]
        self._climb_anim = Animation(climb_frames, speed=5, loop=True)
        self._top_anim = Animation(top_frames, speed=5, loop=True)

    def _init_from_settings(self, settings):
        """Inizializzazione da settings"""
        arthur_config = settings.get_actor_config('arthur')

        # Movement
        movement = arthur_config['movement']
        self._dx = movement['speed_x']
        self._dy = movement['speed_y']

        # Sprites
        sprites = arthur_config['sprites']
        self._default_right = tuple(map(tuple, sprites['default_right']))
        self._default_left = tuple(map(tuple, sprites['default_left']))
        self._jump_right = tuple(map(tuple, sprites['jump_right']))
        self._jump_left = tuple(map(tuple, sprites['jump_left']))

        self._sprite, self._size = self._default_right

        # Jump settings
        jump_config = arthur_config['jump']
        self._jump_cooldown = jump_config['cooldown']
        self._jump_duration = jump_config['duration']

        # Torch settings
        torch_config = arthur_config['torch']
        self._torch_cooldown = torch_config['cooldown']
        self._torch_duration = torch_config['duration']

        # Ladder settings
        ladder_config = arthur_config['ladder']
        self._climb_speed = ladder_config['climb_speed']
        self._ladder_exit_height = ladder_config['exit_height']

        # Animations
        walk_right_data = settings.get_animation_data('arthur', 'walk_right')
        self._walk_right = Animation(
            walk_right_data['frames'],
            speed=walk_right_data['speed'],
            loop=walk_right_data['loop']
        )

        walk_left_data = settings.get_animation_data('arthur', 'walk_left')
        self._walk_left = Animation(
            walk_left_data['frames'],
            speed=walk_left_data['speed'],
            loop=walk_left_data['loop']
        )

        throw_right_data = settings.get_animation_data('arthur', 'throw_right')
        self._throw_right = Animation(
            throw_right_data['frames'],
            speed=throw_right_data['speed'],
            loop=throw_right_data['loop']
        )

        throw_left_data = settings.get_animation_data('arthur', 'throw_left')
        self._throw_left = Animation(
            throw_left_data['frames'],
            speed=throw_left_data['speed'],
            loop=throw_left_data['loop']
        )

        climb_data = settings.get_animation_data('arthur', 'climb')
        self._climb_anim = Animation(
            climb_data['frames'],
            speed=climb_data['speed'],
            loop=climb_data['loop']
        )

        climb_top_data = settings.get_animation_data('arthur', 'climb_top')
        self._top_anim = Animation(
            climb_top_data['frames'],
            speed=climb_top_data['speed'],
            loop=climb_top_data['loop']
        )

    def move(self, arena: Arena):
        old_x, old_y = self._x, self._y
        keys = arena.current_keys()

        if arena.get_intro_running():
            return

        self._handle_movement(keys, arena)
        self._handle_jump(keys, arena)
        self._handle_torch(keys, arena)
        self._handle_collision(keys, arena, old_x, old_y)
        self._handle_gravity()

    def _handle_gravity(self):
        if self._y < 170 and not self._on_ladder:
            self._y = min(170, self._y + 3)

    def _handle_collision(self, keys, arena, old_x, old_y):
        for obj in arena.collisions():
            if isinstance(obj, Zombie):
                pass
                #if not obj.is_harmless():
                    #arena.decrease_lives()
                    #arena.kill(obj)
                    #if arena.get_lives() == 0:
                    #    arena.kill(self)
                    #    arena.set_status(True, "Monster")

            elif isinstance(obj, Eyeball):
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

                    overlap_left = (self._x + arthur_w) - obj_x
                    overlap_right = (obj_x + obj_w) - self._x
                    overlap_top = (self._y + arthur_h) - obj_y
                    overlap_bottom = (obj_y + obj_h) - self._y

                    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                    if min_overlap == overlap_top and self._dy >= 0:
                        self._y = obj_y - arthur_h
                        self._dy = 0
                    elif min_overlap == overlap_bottom:
                        self._y = obj_y + obj_h
                        self._dy = 0
                    elif min_overlap == overlap_left:
                        self._x = obj_x - arthur_w
                    elif min_overlap == overlap_right:
                        self._x = obj_x + obj_w

            elif isinstance(obj, Ladder):
                ladder_x, ladder_y = obj.pos()
                ladder_w, ladder_h = obj.size()
                arthur_w, arthur_h = self._size

                x_on_ladder = (self._x + arthur_w > ladder_x) and (self._x < ladder_x + ladder_w)
                y_on_ladder = (self._y + arthur_h > ladder_y) and (self._y < ladder_y + ladder_h)

                above_ladder = (self._y + arthur_h <= ladder_y + 10) and x_on_ladder

                if self._y < self._ladder_exit_height and self._on_ladder:
                    self._on_ladder = False
                    self._sprite, self._size = (self._default_right if self._facing == "right" else self._default_left)

                if above_ladder and "s" in keys and not self._on_ladder:
                    self._x = ladder_x + ladder_w//2 - arthur_w//2
                    self._on_ladder = True
                elif x_on_ladder and y_on_ladder and "space" in keys and not self._on_ladder:
                    self._x = ladder_x + ladder_w//2 - arthur_w//2
                    self._on_ladder = True
                elif self._on_ladder and not (x_on_ladder and (y_on_ladder or above_ladder)):
                    self._on_ladder = False
                    self._sprite, self._size = (self._default_right if self._facing == "right" else self._default_left)

                if self._on_ladder:
                    if "space" in keys:
                        if self._y > ladder_y:
                            self._y -= self._climb_speed
                            if not self._climb_anim.is_active():
                                self._climb_anim.start()
                            frame = self._climb_anim.update()
                            self._sprite, self._size = frame
                        else:
                            if not self._top_anim.is_active():
                                self._top_anim.start()
                            frame = self._top_anim.update()
                            self._sprite, self._size = frame

                    elif "s" in keys:
                        if self._y + arthur_h < ladder_y + ladder_h:
                            self._y += self._climb_speed
                            if not self._climb_anim.is_active():
                                self._climb_anim.start()
                            frame = self._climb_anim.update()
                            self._sprite, self._size = frame
                        else:
                            self._on_ladder = False
                            self._sprite, self._size = (self._default_right if self._facing == "right" else self._default_left)
                    else:
                        self._climb_anim.stop()
                        self._top_anim.stop()
                        self._sprite, self._size = self._climb_anim.frames()[0]

            elif isinstance(obj, Platform):
                obj_x, obj_y = obj.pos()
                obj_w, obj_h = obj.size()
                arthur_w, arthur_h = self._size

                if (self._x < obj_x + obj_w and self._x + arthur_w > obj_x and
                    self._y + arthur_h > obj_y and self._y + arthur_h < obj_y + obj_h):
                    self._y = obj_y - arthur_h

    def _handle_torch(self, keys, arena):
        current_tick = arena.count()
        if self._on_ladder:
            return

        if self._torch:
            if current_tick - self._torch_time >= self._torch_duration:
                self._torch = False
                self.reset_sprite()
                self._torch_in_cooldown = True
                self._torch_cooldown_time = current_tick
                self._throw_animation.stop()
            else:
                self._sprite, self._size = self._throw_animation.update()

        if current_tick - self._torch_cooldown_time >= self._torch_cooldown:
            self._torch_in_cooldown = False

        if "f" in keys:
            if not self._torch and not self._torch_in_cooldown:
                arena.spawn(Torch(self.pos(), self._facing))
                self._torch = True
                self._torch_time = current_tick

                self._throw_animation = self._throw_right if self._facing == "right" else self._throw_left
                self._sprite, self._size = self._throw_animation.start()

    def _handle_jump(self, keys, arena):
        if self._jumping and arena.count() - self._jump_time >= self._jump_duration:
            self._jumping = False
            self.reset_sprite()
            self._jump_in_cooldown = True
            self._jump_cooldown_time = arena.count()

        if arena.count() - self._jump_cooldown_time >= self._jump_cooldown:
            self._jump_in_cooldown = False

        if "w" in keys and not self._on_ladder:
            if not self._jumping and not self._jump_in_cooldown:
                self._y -= self._dy
                self._jumping = True
                self._jump_time = arena.count()
                self._sprite, self._size = (
                    self._jump_right if self._facing == "right" else self._jump_left
                )

    def _handle_movement(self, keys, arena):
        aw, _ = arena.size()

        if "d" in keys:
            self._x = min((self._x + self._dx), aw)
            self._facing = "right"

            self._walk_left.stop()
            if not self._walk_right.is_active():
                self._walk_right.start()

            if not self._jumping:
                 self._sprite, self._size = self._walk_right.update()
            else:
                self._sprite, self._size = self._jump_right

        elif "a" in keys:
            self._x = max(0, (self._x - self._dx))
            self._facing = "left"

            self._walk_right.stop()
            if not self._walk_left.is_active():
                self._walk_left.start()

            if not self._jumping:
                 self._sprite, self._size = self._walk_left.update()
            else:
                self._sprite, self._size = self._jump_left
        else:
            if not self._jumping:
                self.reset_sprite()

    def reset_sprite(self):
        self._sprite, self._size = self._default_right if self._facing == "right" else self._default_left

    def set_x(self, x):
        self._x = x

    def set_y(self, y):
        self._y = y

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
