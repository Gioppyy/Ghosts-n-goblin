from libs.actor import Actor, Point

class Platform(Actor):
    def __init__(self, pos: Point, size: Point):
        self._x, self._y = pos
        self._w, self._h = size

    def move(self, arena):
        pass

    def pos(self) -> Point:
        return (self._x, self._y)

    def size(self) -> Point:
        return (self._w, self._h)

    def sprite(self) -> Point | None:
        return None
