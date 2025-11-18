from actors.gravestone import Gravestone, Ladder, Platform
from libs.animation import Animation
from actors.zombie import Zombie
from actors.arthur import Arthur
from actors.plant import Plant
from libs.actor import Arena
from libs.settings import Settings
from random import randint

import libs.g2d as g2d

class GngGui():
    def __init__(self, arena: Arena | None):
        self._x_view, self._y_view = 0, 0
        self._arena = arena

        self._settings = arena.get_settings()

        W_VIEW, H_VIEW = self._settings.get_view_size()
        self._w_view, self._h_view = W_VIEW, H_VIEW
        self._bg_width, self._bg_height = self._settings.get_bg_size()
        self._change_song_x = self._settings.get_song_change_x()

        self._gameover_anim_finished = False
        gameover_data = self._settings.get_gameover_config()
        gameover_frames = [tuple(map(tuple, frame)) for frame in gameover_data['animation']['frames']]
        self._gameover_anim = Animation(
            gameover_frames,
            loop=False,
            speed=gameover_data['animation']['speed']
        )
        self._gameover_anim.set_on_complete(self.finish_gameover)
        self._gameover_pos = tuple(gameover_data['position'])

        lives_config = self._settings.get_game_setting('lives')
        self._live_sprite = tuple(lives_config['sprite'])
        self._live_size = lives_config['size']
        self._live_pos_y = lives_config['position_y']
        self._live_pos_x_start = lives_config['position_x_start']

        camera_config = self._settings.get_game_setting('camera')
        self._scroll_speed = camera_config['scroll_speed']
        self._camera_margin = camera_config['margin']

        zombie_config = self._settings.get_zombie_spawn_config()
        self._zombie_spawn_chance = zombie_config['chance']
        self._zombie_spawn_target = zombie_config['target']
        self._zombie_dist_min = zombie_config['distance_min']
        self._zombie_dist_max = zombie_config['distance_max']
        self._zombie_y = zombie_config['y_position']

        g2d.init_canvas((self._w_view, self._h_view), 2)
        g2d.main_loop(self.tick)

    def tick(self):
        g2d.clear_canvas()
        g2d.set_color((0,0,0))
        g2d.draw_image(
            self._settings.get_img('background'),
            (0, 0),
            (self._x_view, self._y_view),
            (self._w_view, self._h_view)
        )

        finished, winner = self._arena.get_status()
        if finished:
            self.show_result(winner)
            return

        keys = self._arena.current_keys()
        left_key = self._settings.get_key('left')
        right_key = self._settings.get_key('right')

        if left_key in keys and self._x_view > 0:
            self._x_view = max(0, self._x_view - self._scroll_speed)
        elif right_key in keys and self._x_view < self._bg_width - self._w_view:
            self._x_view = min(self._bg_width - self._w_view, self._x_view + self._scroll_speed)

        for live in range(self._arena.get_lives()):
            g2d.draw_image(
                self._settings.get_sprite_sheet(),
                (self._live_pos_x_start + self._live_size * live, self._live_pos_y),
                self._live_sprite,
                (self._live_size, self._live_size)
            )

        for a in self._arena.actors():
            ax, ay = a.pos()
            if isinstance(a, Arthur):

                if ax >= self._change_song_x and ("start" in self._arena.get_song_src()):
                    self._arena.set_song(self._settings.get_audio('end'))
                    self._arena.start_song()

                # Spawn a zombie only if arthur is alive
                if randint(0, self._zombie_spawn_chance) == self._zombie_spawn_target:
                    direction = randint(0, 10) % 2
                    diff = randint(self._zombie_dist_min, self._zombie_dist_max)
                    zx = ax + diff * (1 if direction == 0 else -1)
                    self._arena.spawn(Zombie((max(0, zx), self._zombie_y), direction, self._arena))

                g2d.draw_image(
                    self._settings.get_sprite_sheet(),
                    (ax - self._x_view, ay - self._y_view),
                    a.sprite(),
                    a.size(),
                )

                if ax - self._x_view < self._camera_margin:
                    self._x_view = max(0, ax - self._camera_margin)
                elif ax - self._x_view > self._w_view - self._camera_margin:
                    self._x_view = min(self._bg_width - self._w_view, ax - (self._w_view - self._camera_margin))
            else:
                if a.sprite() != None:
                    g2d.draw_image(
                        self._settings.get_sprite_sheet(),
                        (ax - self._x_view, ay - self._y_view),
                        a.sprite(),
                        a.size(),
                    )

        self._arena.tick(g2d.current_keys())

    def finish_gameover(self):
        self._gameover_anim.stop()
        self._gameover_anim_finished = True

    def show_result(self, winner):
        if not self._gameover_anim_finished:
            if not self._gameover_anim.is_active():
                self._gameover_anim.start()
            else:
                pos, size = self._gameover_anim.update()
                g2d.draw_image(
                    self._settings.get_img('gameover'),
                    self._gameover_pos,
                    pos,
                    size
                )
            return

        if winner == "Monster":
            g2d.draw_image(self._settings.get_img('lose'), (0, 0))
        else:
            g2d.draw_image(self._settings.get_img('win'), (0, 0))

class GngGame(Arena):
    def __init__(self):
        self._settings = Settings()

        view_size = self._settings.get_view_size()
        bg_size = self._settings.get_bg_size()

        super().__init__(view_size, bg_size)
        self._status = (False, "")
        self._current_song_src = None
        self._lives = self._settings.get_initial_lives()

        # Load platforms
        for platform_data in self._settings.get_platforms():
            self.spawn(Platform(tuple(platform_data['pos']), tuple(platform_data['size'])))

        # Load Arthur
        self.spawn(Arthur(self._settings.get_arthur_start()))

        # Load gravestones
        for gravestone_data in self._settings.get_gravestones():
            self.spawn(Gravestone((gravestone_data['x'], gravestone_data['y'])))

        # Load plants
        for plant_data in self._settings.get_plants():
            self.spawn(Plant((plant_data['x'], plant_data['y']), self))

        # Load ladders
        for ladder_data in self._settings.get_ladders():
            self.spawn(Ladder((ladder_data['x'], ladder_data['y'])))

        self.set_song(self._settings.get_audio('start'))
        self.start_song()

    def get_settings(self):
        return self._settings

    def get_song(self):
        return self._current_song_src

    def get_song_src(self) -> str | None:
        return self._current_song_src

    def set_song(self, song_src: str):
        if self._current_song_src is not None:
            g2d.pause_audio(self._current_song_src)
        self._current_song_src = song_src

    def start_song(self):
        g2d.play_audio(self._current_song_src)

    def give_lives(self, amount = 1):
        self._lives += amount

    def decrease_lives(self):
        self._lives -= 1

    def get_lives(self):
        return self._lives

    def set_status(self, status, winner):
        self._status = (status, winner)

    def get_status(self):
        return self._status

def main():
    global gui
    game = GngGame()
    gui = GngGui(game)

if __name__ == "__main__":
    main()
