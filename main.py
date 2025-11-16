from libs.actor import Arena
from actors.arthur import Arthur
from actors.zombie import Zombie
from actors.gravestone import Gravestone, Ladder, Platform
from actors.plant import Plant
from random import randint

import libs.g2d as g2d

BG_WIDTH, BG_HEIGHT = 3588, 250
CHANGE_SONG_X = 1794
W_VIEW, H_VIEW = 400, 220

class GngGui():
    def __init__(self, arena: Arena | None):
        self._x_view, self._y_view = 0, 0
        self._arena = arena

        g2d.init_canvas((W_VIEW, H_VIEW), 2)
        g2d.main_loop(self.tick)

    def tick(self):
        g2d.clear_canvas()
        g2d.set_color((0,0,0))
        g2d.draw_image("./imgs/background.png", (0, 0), (self._x_view, self._y_view), (W_VIEW, H_VIEW))

        finished, winner = self._arena.get_status()
        if finished:
            self.show_result(winner)
            return

        keys = self._arena.current_keys()
        if "left" in keys and self._x_view > 0:
            self._x_view = max(0, self._x_view - 5)
        elif "right" in keys and self._x_view < BG_WIDTH - W_VIEW:
            self._x_view = min(BG_WIDTH - W_VIEW, self._x_view + 5)

        for a in self._arena.actors():
            ax, ay = a.pos()
            if isinstance(a, Arthur):

                if ax >= CHANGE_SONG_X and ("start" in self._arena.get_song_src()):
                    self._arena.set_song("./audio/end.mp3")
                    self._arena.start_song()

                # Spawn a zombie only if arthur is alive
                if randint(0, 500) == 250:
                    direction = randint(0, 10) % 2
                    diff = randint(50, 200)
                    zx = ax + diff * (1 if direction == 0 else -1)
                    self._arena.spawn(Zombie((max(0, zx), 170), direction))

                g2d.draw_image(
                    "./imgs/sprites.png",
                    (ax - self._x_view, ay - self._y_view),
                    a.sprite(),
                    a.size(),
                )

                margin = 50
                if ax - self._x_view < margin:
                    self._x_view = max(0, ax - margin)
                elif ax - self._x_view > W_VIEW - margin:
                    self._x_view = min(BG_WIDTH - W_VIEW, ax - (W_VIEW - margin))
            else:
                if a.sprite() != None:
                    g2d.draw_image(
                        "./imgs/sprites.png",
                        (ax - self._x_view, ay - self._y_view),
                        a.sprite(),
                        a.size(),
                    )

        self._arena.tick(g2d.current_keys())

    def show_result(self, winner):
        if winner == "Monster":
            g2d.draw_image("./imgs/lose.png", (0, 0))
        else:
            g2d.draw_image("./imgs/win.png", (0, 0))

class GngGame(Arena):
    def __init__(self):
        super().__init__((W_VIEW, H_VIEW), (BG_WIDTH, BG_HEIGHT))

        self._status = (False, "")
        self._current_song_src = None
        self._lives = 3

        self.spawn(Platform((0, 205), (3588, 30))) # piattaforma di base
        self.spawn(Platform((610, 120), (525, 15))) # piattaforma centrale

        # crea i personaggi
        self.spawn(Arthur((0, 170)))
        for x in [50, 242, 530, 754, 962, 1106]:
            self.spawn(Gravestone((x, 185)))
        for x, y in [(1108, 98)]:
            self.spawn(Plant((x, y)))
        for x in [722, 914, 1074]: # posizioni delle tombe
            self.spawn(Ladder((x, 122)))

        # gestisce la canzone iniziale
        self.set_song("./audio/start.mp3")
        self.start_song()

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
