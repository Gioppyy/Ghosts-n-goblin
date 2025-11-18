from libs.actor import Arena
import libs.g2d as g2d
from actors.arthur import Arthur
from actors.princess import Princess, Devil
from actors.gravestone import Platform
from libs.gng_manager import GngGame, GngGui

W_VIEW, H_VIEW = 400, 220
BG_WIDTH, BG_HEIGHT = 3588, 230

ARTHUR_JUMP_LEFT = ((336, 29), (32, 27))
ARTHUR_ARMOR = ((80, 170), (25, 30))
ARTHUR_JUMP_DURATION = 24

class State:
    TITLE = "title_screen"
    WAIT = "wait"
    FADE = "fade"
    SPAWN_DEVIL = "spawn_devil"
    DEVIL = "devil"
    ARTHUR = "arthur"
    ARMOR = "armor"
    END = "end"

class Intro:
    def __init__(self):
        self._state = State.TITLE
        self._fade = 0

        self._wait_tick = 0

        self._arena = Arena((W_VIEW, H_VIEW), (BG_WIDTH, BG_HEIGHT))
        self._arena.spawn(Platform((0, 205), (3588, 30)))
        self._arena.set_intro_running(True)

        self._arthur = Arthur((100, 172))
        self._princess = Princess((130, 170))
        self._devil = Devil((235, 70), self._princess)

        self._arena.spawn(self._arthur)
        self._arena.spawn(self._princess)

        self._devil_spawned = False
        self._arthur_jump_tick = 0
        self._armor_timer = 0

    def draw_actors(self):
        for actor in self._arena.actors():
            ax, ay = actor.pos()
            spr = actor.sprite()
            size = actor.size()
            if spr is not None:
                g2d.draw_image("./imgs/sprites.png", (ax, ay), spr, size)

    def tick(self):
        g2d.clear_canvas()

        if self._state == State.TITLE:
            self._handle_enter_state()
            return

        match self._state:
            case State.WAIT:
                self._handle_wait_state()
            case State.FADE:
                self._handle_fade_state()
            case State.SPAWN_DEVIL:
                self._handle_spawn_devil_state()
            case _:
                pass

        if self._state in (State.DEVIL, State.ARTHUR, State.ARMOR, State.END):
            g2d.set_color((0, 0, 0))
            g2d.draw_rect((0, 0), (W_VIEW, H_VIEW))

        self._arena.tick(g2d.current_keys())
        self.draw_actors()

        if self._state == State.DEVIL:
            self._handle_devil_state()
        elif self._state == State.ARTHUR:
            self._handle_arthur_state()
        elif self._state == State.ARMOR:
            self._handle_armor_state()
        elif self._state == State.END:
            self._handle_end_state()

    def _handle_enter_state(self):
        g2d.draw_image("./imgs/title_screen.png", (0, 0), (0, 0), (W_VIEW, H_VIEW))
        keys = g2d.current_keys()
        if "return" in keys:
            self._state = State.WAIT

    def _handle_wait_state(self):
        g2d.draw_image("./imgs/background.png", (0, 0), (0, 0), (W_VIEW, H_VIEW))
        self._wait_tick += 1
        if self._wait_tick > 40:
            self._state = State.FADE

    def _handle_fade_state(self):
        g2d.draw_image("./imgs/background.png", (0, 0), (0, 0), (W_VIEW, H_VIEW))
        self._fade = min(255, self._fade + 6)
        g2d.set_color((0, 0, 0, self._fade))
        g2d.draw_rect((0, 0), (W_VIEW, H_VIEW))
        if self._fade >= 255:
            self._state = State.SPAWN_DEVIL

    def _handle_spawn_devil_state(self):
        if not self._devil_spawned:
            self._arena.spawn(self._devil)
            self._devil_spawned = True
        self._state = State.DEVIL

    def _handle_devil_state(self):
        devil_x, devil_y = self._devil.pos()
        arthur_x, arthur_y = self._arthur.pos()

        dx = abs(devil_x - arthur_x)
        dy = abs(devil_y - arthur_y)
        if (dx < 60 and dy < 60 and self._arthur_jump_tick == 0) or self._princess.captured() and self._arthur_jump_tick == 0:
            self._arthur_jump_tick = ARTHUR_JUMP_DURATION
            self._state = State.ARTHUR

    def _handle_arthur_state(self):
        arthur_x, arthur_y = self._arthur.pos()
        if self._arthur_jump_tick > 0:
            if self._arthur_jump_tick > 10:
                self._arthur.set_x(arthur_x-2)
                self._arthur.set_y(arthur_y-3)
            else:
                self._arthur.set_x(arthur_x-1)
                self._arthur.set_y(arthur_y+3)

            self._arthur._sprite, self._arthur._size = ARTHUR_JUMP_LEFT
            self._arthur_jump_tick -= 1
        else:
            self._armor_timer = 0
            self._state = State.ARMOR

    def _handle_armor_state(self):
        self._arthur._sprite, self._arthur._size = ARTHUR_ARMOR
        self._armor_timer += 1
        if self._armor_timer > 40:
            self._state = State.END

    def _handle_end_state(self):
        try:
            self._arena.set_intro_running(False)
            g2d.pause_audio("./audio/intro.mp3")
            game = GngGame()
            gui = GngGui(game)

        except Exception as e:
            import traceback
            traceback.print_exc()
            g2d.close_canvas()

def main():
    g2d.init_canvas((W_VIEW, H_VIEW), 2)
    g2d.play_audio("./audio/intro.mp3", loop=True, volume=0.06)

    intro = Intro()
    g2d.main_loop(intro.tick)

if __name__ == "__main__":
    main()
