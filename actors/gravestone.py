from libs.actor import Actor, Arena, Point

class Gravestone(Actor):
    def __init__(self, pos: Point):
        self._x, self._y = pos

    def move(self, arena):
        pass

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return (15, 15)

    def sprite(self) -> Point | None:
        return None
