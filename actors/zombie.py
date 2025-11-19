from libs.actor import Actor, Arena, Point
from random import randint
from libs.animation import Animation

class Zombie(Actor):
    def __init__(self, pos, direction, arena):
        self._x, self._y = pos
        self._dir = direction
        self._phase = "spawn"  # spawn, walk, death
        self._harmless = True  # Innocuo durante spawn e death

        # Carica settings
        settings = arena.get_settings()
        zombie_config = settings.get_actor_config('zombie')

        # Parametri
        self._speed = zombie_config['speed']
        self._distance = randint(zombie_config['distance_min'], zombie_config['distance_max'])
        self._move_down_speed = zombie_config['move_down_speed']

        # Carica animazioni in base alla direzione
        if self._dir == 0:  # left
            walk_data = settings.get_animation_data('zombie', 'walk_left')
            death_data = settings.get_animation_data('zombie', 'death_left')
        else:  # right
            walk_data = settings.get_animation_data('zombie', 'walk_right')
            death_data = settings.get_animation_data('zombie', 'death_right')

        # Crea animazioni
        self._walk_anim = Animation(
            walk_data['frames'],
            speed=walk_data['speed'],
            loop=walk_data['loop']
        )

        self._death_anim = Animation(
            death_data['frames'],
            speed=death_data['speed'],
            loop=False,
            on_update=self.move_down
        )

        # Animazione spawn: frames di morte al contrario
        spawn_frames = list(reversed(death_data['frames']))
        self._spawn_anim = Animation(
            spawn_frames,
            speed=death_data['speed'],
            loop=False,
            on_update=self.move_up
        )

        # Calcola l'altezza totale dell'animazione di morte per posizionare correttamente lo spawn
        # Lo zombie deve iniziare completamente sotto terra
        total_movement = len(spawn_frames) * self._move_down_speed
        self._y += total_movement

        # Inizia con l'animazione di spawn
        self._sprite, self._size = self._spawn_anim.start()

        self._dx = self._speed if self._dir == 1 else -self._speed

    def is_harmless(self):
        """Ritorna True se lo zombie è innocuo (durante spawn o death)"""
        return self._harmless

    def move(self, arena: Arena):
        if self._phase == "spawn":
            self._sprite, self._size = self._spawn_anim.update()
            # Quando l'animazione di spawn finisce, passa a walk
            if not self._spawn_anim.is_active():
                self._phase = "walk"
                self._harmless = False  # Ora diventa pericoloso
                self._walk_anim.start()

        elif self._phase == "walk":
            self._sprite, self._size = self._walk_anim.update()
            self._x += self._dx
            self._distance -= abs(self._dx)

            # Controlla se deve morire
            if self._x <= 0 or self._distance <= 0:
                self._phase = "death"
                self._harmless = True  # Diventa innocuo durante la morte
                self._death_anim.start()
                self._walk_anim.stop()
                self._dx = 0

        elif self._phase == "death":
            self._sprite, self._size = self._death_anim.update()
            # Quando l'animazione di morte finisce, si uccide
            if not self._death_anim.is_active():
                arena.kill(self)

    def move_down(self):
        """Callback per l'animazione di morte"""
        self._y += self._move_down_speed

    def move_up(self):
        """Callback per l'animazione di spawn (sale dal terreno)"""
        self._y -= self._move_down_speed

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
