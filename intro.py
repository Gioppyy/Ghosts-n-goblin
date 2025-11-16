from libs.actor import Arena
import libs.g2d as g2d
from actors.arthurold import Arthur
from actors.princess import Princess, Devil
from actors.gravestone import Platform

# Constants
W_VIEW, H_VIEW = 400, 220
BG_WIDTH, BG_HEIGHT = 3588, 250

ARTHUR_JUMP_LEFT = ((336, 29), (32, 27))
ARTHUR_ARMOR = ((80, 170), (25, 30))

# Game states
STATE_WAIT = "wait"
STATE_FADE = "fade"
STATE_SPAWN_DEVIL = "spawn_devil"
STATE_DEVIL = "devil"
STATE_ARTHUR = "arthur"
STATE_ARMOR = "armor"
STATE_END = "end"

# Global variables
state = STATE_WAIT
fade_alpha = 0
tick_count = 0
arthur_jump_tick = 0
armor_timer = 0
devil_spawned = False

arena = None
arthur = None
princess = None
devil = None


def handle_wait_state():
    global state, tick_count
    g2d.draw_image("./imgs/background.png", (0, 0), (0, 0), (W_VIEW, H_VIEW))
    tick_count += 1
    if tick_count > 40:
        state = STATE_FADE


def handle_fade_state():
    global state, fade_alpha
    g2d.draw_image("./imgs/background.png", (0, 0), (0, 0), (W_VIEW, H_VIEW))
    fade_alpha = min(255, fade_alpha + 6)
    g2d.set_color((0, 0, 0, fade_alpha))
    g2d.draw_rect((0, 0), (W_VIEW, H_VIEW))
    if fade_alpha >= 255:
        state = STATE_SPAWN_DEVIL


def handle_spawn_devil_state():
    global state, devil_spawned
    if not devil_spawned:
        devil._x, devil._y = 235, 70
        arena.spawn(devil)
        devil_spawned = True
    state = STATE_DEVIL


def handle_devil_state():
    global state, arthur_jump_tick

    dx = abs(devil._x - arthur._x)
    dy = abs(devil._y - arthur._y)

    if (dx < 60 and dy < 60 and arthur_jump_tick == 0) or (getattr(princess, "_captured", False) and arthur_jump_tick == 0):
        arthur_jump_tick = 24
        state = STATE_ARTHUR


def handle_arthur_state():
    global state, arthur_jump_tick, armor_timer

    if arthur_jump_tick > 0:
        half = 10
        if arthur_jump_tick > half:
            arthur._x -= 2
            arthur._y -= 3
        else:
            arthur._x -= 1
            arthur._y += 3

        arthur._sprite, arthur._size = ARTHUR_JUMP_LEFT
        arthur_jump_tick -= 1
    else:
        armor_timer = 0
        state = STATE_ARMOR
        try:
            g2d.play_audio("./audio/armor_on.wav")
        except Exception:
            pass


def handle_armor_state():
    global state, armor_timer

    arthur._sprite, arthur._size = ARTHUR_ARMOR
    armor_timer += 1
    if armor_timer > 40:
        state = STATE_END


def handle_end_state():
    try:
        import main as game_main
        g2d.pause_audio("./audio/intro.mp3")
        game_main.main()
    except Exception as e:
        print(e)
        g2d.close_canvas()

def draw_actors():
    for actor in arena.actors():
        ax, ay = actor.pos()
        spr = actor.sprite()
        size = actor.size()
        if spr is not None:
            g2d.draw_image("./imgs/sprites.png", (ax, ay), spr, size)


def tick():
    global state

    g2d.clear_canvas()

    handle_end_state()

    # Handle game states
    if state == STATE_WAIT:
        handle_wait_state()
    elif state == STATE_FADE:
        handle_fade_state()
    elif state == STATE_SPAWN_DEVIL:
        handle_spawn_devil_state()
    elif state in (STATE_DEVIL, STATE_ARTHUR, STATE_ARMOR, STATE_END):
        g2d.set_color((0, 0, 0))
        g2d.draw_rect((0, 0), (W_VIEW, H_VIEW))

    # Update arena and draw actors
    arena.tick([])
    draw_actors()

    # Handle specific state logic after drawing
    if state == STATE_DEVIL:
        handle_devil_state()
    elif state == STATE_ARTHUR:
        handle_arthur_state()
    elif state == STATE_ARMOR:
        handle_armor_state()
    elif state == STATE_END:
        handle_end_state()


def initialize_game():
    global arena, arthur, princess, devil

    arena = Arena((W_VIEW, H_VIEW), (BG_WIDTH, BG_HEIGHT))
    arena.spawn(Platform((0, 205), (3588, 30)))

    arthur = Arthur((100, 172))
    princess = Princess((130, 170))
    devil = Devil((235, 70), princess)

    arena.spawn(arthur)
    arena.spawn(princess)


def main():
    initialize_game()

    g2d.init_canvas((W_VIEW, H_VIEW), 2)

    try:
        g2d.play_audio("./audio/intro.mp3", loop=True, volume=0.06)
    except Exception as e:
        print(e)
        pass

    g2d.main_loop(tick)


if __name__ == "__main__":
    main()
