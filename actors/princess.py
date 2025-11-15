from libs.actor import Actor, Arena, Point

FRAMES = [((539, 609), (18, 30)), ((557, 609), (18, 30)), ((575, 609), (18, 30)), ((593, 609), (18, 30)), ((610, 609), (18, 30)), ((627, 609), (25, 30)),]
SPAWN = [((531, 302), (42, 32)), ((607, 335), (45, 30))]
FLY = [((560, 336), (35, 30)), ((562, 240), (26, 28))]

class Princess(Actor):
    def __init__(self, pos: Point):
        self._x, self._y = pos
        self._frame = 0
        self._timer = 0
        self._sprite, self._size = FRAMES[self._frame]
        self._captured = False
        self._alerted = False # inizia a spaventarsi quando arriva il diavolo
        self._animation_done = False 

    def move(self, arena: Arena):
        if self._captured:
            for actor in arena.actors():
                if isinstance(actor, Devil) and actor._phase == "fly":
                    self._x = actor._x
                    self._y = actor._y
            return

        for actor in arena.actors():
            if isinstance(actor, Devil) and actor._phase == "spawn":
                self._alerted = True

        if self._alerted and not self._animation_done:
            self._timer += 1
            if self._timer % 15 == 0: 
                if self._frame < len(FRAMES) - 1:
                    self._frame += 1
                    self._sprite, self._size = FRAMES[self._frame]
                else:
                    self._animation_done = True
                    self._sprite, self._size = FRAMES[-1]

    def capture(self):
        self._captured = True

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite

class Devil(Actor):
    def __init__(self, pos: Point, target: Actor | None = None):
        self._x, self._y = pos
        self._target = target
        self._sprite, self._size = SPAWN[0]
        self._frame = 0
        self._phase = "spawn"
        self._tick = 0
        self._dx, self._dy = 2, -1  
        
    def move(self, arena: Arena):
        self._tick += 1

        if self._phase == "spawn":
            if self._tick % 10 == 0:
                self._frame = (self._frame + 1) % len(SPAWN)
                self._sprite, self._size = SPAWN[self._frame]
            if self._tick > 40:
                self._phase = "grab"
                self._tick = 0

        elif self._phase == "grab":
            if self._target:
                tx, ty = self._target.pos()
                step = 2
                self._x += step if self._x < tx else -step
                self._y += step if self._y < ty else -step

                if abs(self._x - tx) < 5 and abs(self._y - ty) < 5:
                    self._target.capture()  
                    self._phase = "fly"
                    self._tick = 0

        elif self._phase == "fly":
            self._x += self._dx
            self._y += self._dy
            if self._tick % 8 == 0:
                self._frame = (self._frame + 1) % len(FLY)
                self._sprite, self._size = FLY[self._frame]

            if self._y < -50:
                arena.kill(self)

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return self._size

    def sprite(self) -> Point | None:
        return self._sprite
