from libs.actor import Arena
from actors.arthur import Arthur
from actors.zombie import Zombie
from actors.gravestone import Gravestone
from actors.plant import Plant
from random import randint

BG_WIDTH, BG_HEIGHT = 3588, 250
playing = "start"

def show_result(winner):
    global written

    if winner == "Monster":
        g2d.draw_image("./imgs/lose.png", (0, 0))
    else:
        g2d.draw_image("./imgs/win.png", (0, 0))

def tick():
    global x_view, y_view, playing

    g2d.clear_canvas()
    g2d.set_color((0,0,0))
    g2d.draw_image("./imgs/background.png", (0, 0), (x_view, y_view), (w_view, h_view))

    finished, winner = arena.get_status()
    if not finished:
        show_result(winner)
        return

    keys = arena.current_keys()
    if "left" in keys and x_view > 0:
        x_view = max(0, x_view - 5)
    elif "right" in keys and x_view < BG_WIDTH - w_view:
        x_view = min(BG_WIDTH - w_view, x_view + 5)

    for a in arena.actors():
        ax, ay = a.pos()
        if isinstance(a, Arthur):

            if ax >= 1794 and ("start" in arena.get_song_src()):
                arena.set_song("./audio/end.mp3")
                arena.start_song()

            # Spawn a zombie only if arthur is alive
            if randint(0, 500) == 250:
                direction = randint(0, 10) % 2
                diff = randint(50, 200)
                zx = ax + diff * (1 if direction == 0 else -1)
                arena.spawn(Zombie((max(0, zx), 170), direction))

            if a.sprite != None:
                g2d.draw_image(
                    "./imgs/sprites.png",
                    (ax - x_view, ay - y_view),
                    a.sprite(),
                    a.size(),
                )

            margin = 50
            if ax - x_view < margin:
                x_view = max(0, ax - margin)
            elif ax - x_view > w_view - margin:
                x_view = min(BG_WIDTH - w_view, ax - (w_view - margin))
        else:
            if a.sprite() != None:
                g2d.draw_image(
                    "./imgs/sprites.png",
                    (ax - x_view, ay - y_view),
                    a.sprite(),
                    a.size(),
                )

    arena.tick(g2d.current_keys())

x_view, y_view = 0, 0
w_view, h_view = 400, 220

def main():
    global g2d, arena
    import libs.g2d as g2d
    arena = Arena((w_view, h_view), (BG_WIDTH, BG_HEIGHT))

    arena.spawn(Arthur((0, 170)))
    for x in [50, 242, 530, 754, 962, 1106]: # posizioni delle tombe
        arena.spawn(Gravestone((x, 185)))

    for x,y in [(1108, 98)]:
        arena.spawn(Plant((x, y)))

    g2d.init_canvas(arena.view_size(), 2)
    arena.set_song("./audio/start.mp3")
    arena.start_song()

    g2d.main_loop(tick)

if __name__ == "__main__":
    main()
