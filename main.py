from libs.actor import Arena
from actors.arthur import Arthur
from actors.zombie import Zombie
from actors.gravestone import Gravestone
from actors.plant import Plant
from random import randint

BG_WIDTH, BG_HEIGHT = 3588, 250
W_VIEW, H_VIEW = 400, 220

class GngGui():
    def __init__(self):
        self._width, self._height = (BG_WIDTH, BG_HEIGHT)
        self._w_view, self._h_view = (W_VIEW, H_VIEW)
        self._x_view, self._y_view = 0, 0

        self._arena = Arena((self._w_view, self._h_view), (self._width, self._height))
        self._status = (False, "")

    def tick(self):
        g2d.clear_canvas()
        g2d.set_color((0,0,0))
        g2d.draw_image("./imgs/background.png", (0, 0), (self._x_view, self._y_view), (self._w_view, self._h_view))

        # da spostare in gng-game
        finished, winner = self.get_status()
        if finished:
            self.show_result(winner)
            return

        # movimento della telecamera
        keys = self._arena.current_keys()
        if "left" in keys and self._x_view > 0:
            self._x_view = max(0, self._x_view - 5)
        elif "right" in keys and self._x_view < BG_WIDTH - self._w_view:
            self._x_view = min(BG_WIDTH - self._w_view, self._x_view + 5)

        for a in self._arena.actors():
            ax, ay = a.pos()
            if isinstance(a, Arthur):

                if ax >= 1794 and ("start" in self._arena.get_song_src()):
                    self._arena.set_song("./audio/end.mp3")
                    self._arena.start_song()

                # Spawn a zombie only if arthur is alive
                if randint(0, 500) == 250:
                    direction = randint(0, 10) % 2
                    diff = randint(50, 200)
                    zx = ax + diff * (1 if direction == 0 else -1)
                    self._arena.spawn(Zombie((max(0, zx), 170), direction))

                if a.sprite != None:
                    g2d.draw_image(
                        "./imgs/sprites.png",
                        (ax - self._x_view, ay - self._y_view),
                        a.sprite(),
                        a.size(),
                    )

                margin = 50
                if ax - self._x_view < margin:
                    self._x_view = max(0, ax - margin)
                elif ax - self._x_view > self._w_view - margin:
                    self._x_view = min(BG_WIDTH - self._w_view, ax - (self._w_view - margin))
            else:
                if a.sprite() != None:
                    g2d.draw_image(
                        "./imgs/sprites.png",
                        (ax - self._x_view, ay - self._y_view),
                        a.sprite(),
                        a.size(),
                    )

        self._arena.tick(g2d.current_keys())

    def set_status(self, status, winner):
        self._status = (status, winner)

    def get_status(self):
        return self._status

    def view_size(self):
        return (self._w_view, self._h_view)

    def show_result(self, winner):
        if winner == "Monster":
            g2d.draw_image("./imgs/lose.png", (0, 0))
        else:
            g2d.draw_image("./imgs/win.png", (0, 0))

def tick():
    gui.tick()

def main():
    global g2d, gui
    import libs.g2d as g2d

    gui = GngGui()

    gui._arena.spawn(Arthur((0, 170)))
    for x in [50, 242, 530, 754, 962, 1106]: # posizioni delle tombe
        gui._arena.spawn(Gravestone((x, 185)))

    for x,y in [(1108, 98)]:
        gui._arena.spawn(Plant((x, y)))

    g2d.init_canvas(gui.view_size(), 2)
    gui._arena.set_song("./audio/start.mp3")
    gui._arena.start_song()

    g2d.main_loop(tick)

if __name__ == "__main__":
    main()
