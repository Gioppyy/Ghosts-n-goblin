#!/usr/bin/env python3
"""
@author  Michele Tomaiuolo - http://www.ce.unipr.it/people/tomamic
@license This software is free - http://www.gnu.org/licenses/gpl.html
"""

import libs.g2d as g2d

Point = tuple[float, float]

class Actor:
    """Interface to be implemented by each game character.
    """
    def move(self, arena: "Arena"):
        """Called by Arena, at the actor’s turn.
        """
        raise NotImplementedError("Abstract method")

    def pos(self) -> Point:
        """Return the position (x, y) of the actor (left-top corner).
        """
        raise NotImplementedError("Abstract method")

    def size(self) -> Point:
        """Return the size (w, h) of the actor.
        """
        raise NotImplementedError("Abstract method")

    def sprite(self) -> Point | None:
        """Return the position (x, y) of current sprite,
        if it is contained in a larger image, with other sprites;
        Otherwise, simply return None.
        """
        raise NotImplementedError("Abstract method")


def check_collision(a1: Actor, a2: Actor) -> bool:
    """Check two actors (args) for mutual collision or contact,
    according to bounding-box collision detection.
    Return True if actors collide or touch, False otherwise.
    """
    x1, y1, w1, h1 = a1.pos() + a1.size()
    x2, y2, w2, h2 = a2.pos() + a2.size()
    return (y2 <= y1 + h1 and y1 <= y2 + h2 and
            x2 <= x1 + w1 and x1 <= x2 + w2)


class Arena():
    """A generic 2D game, with a given size in pixels and a list of actors.
    """
    def __init__(self, view: Point,  size: Point):
        """Create an arena, with given dimensions in pixels.
        """
        self._w, self._h = size
        self._w_view, self._h_view = view
        self._count = 0
        self._turn = -1
        self._actors = []
        self._curr_keys = self._prev_keys = tuple()
        self._collisions = []
        self._score = 0
        self._level = 0
        self._lives = 3
        self._status = (True, "")
        self._current_song_src = None

    def spawn(self, a: Actor):
        """Register an actor into this arena.
        Actors are blitted in their order of registration.
        """
        if a not in self._actors:
            self._actors.append(a)

    def kill(self, a: Actor):
        """Remove an actor from this arena.
        """
        if a in self._actors:
            self._actors.remove(a)

    def kill_all(self):
        for a in self._actors:
            self.kill(a)

    def kill_all(self, type):
        for a in self._actors:
            if isinstance(a, type):
                self.kill(a)

    def set_status(self, status, winner):
        self._status = (status, winner)

    def get_status(self):
        return self._status

    def give_lives(self, amount = 1):
        self._lives += amount

    def decrease_lives(self):
        self._lives -= 1

    def get_lives(self):
        return self._lives

    def get_song(self):
        return self._current_song

    def get_song_src(self) -> str | None:
        return self._current_song_src

    def set_song(self, song_src: str):
        if self._current_song_src != None:
            g2d.pause_audio(self._current_song_src)
        self._current_song_src = song_src

    def start_song(self):
        g2d.play_audio(self._current_song_src)

    def spawn_mobs(self, type):
        self.kill_all(type)
        for y in range(2+(1*self.get_level())):
            for x in range(4+(1*self.get_level())):
                self.spawn(type((x * 42, (y * 24)+200)))

    def there_are_alive_mobs(self, type):
        return any(isinstance(actor, type) for actor in self._actors)

    def get_amount_of(self, type):
        count = 0
        for a in self._actors:
            if isinstance(a, type):
                count += 1
        return count

    def get_by_type(self, type):
        for a in self._actors:
            if isinstance(a, type):
                return a
        return None

    def set_score(self, score: int):
        self._score = score

    def get_score(self) -> (int):
        return self._score

    def increase_level(self):
        self._level += 1

    def get_level(self) -> (int):
        return self._level

    def tick(self, keys=[]):
        """Move all actors (through their own move method).
        """
        actors = list(reversed(self._actors))
        self._detect_collisions(actors)
        self._prev_keys = self._curr_keys
        self._curr_keys = keys
        for self._turn, a in enumerate(actors):
            a.move(self)
        self._count += 1

    def _naive_collisions(self, actors):
        # self._collisions = [[a2 for a2 in actors if a1 is not a2 and check_collision(a1, a2)] for a1 in actors]
        self._collisions.clear()
        for a1 in actors:
            colls1 = []
            for a2 in actors:
                if a1 is not a2 and check_collision(a1, a2):
                    colls1.append(a2)
            self._collisions.append(colls1)

    def _detect_collisions(self, actors):
        self._collisions.clear()
        # divide the arena in tiles, for efficient collision detection
        tile = 40
        nx, ny = -(-self._w // tile),  -(-self._h // tile)  # ceil div
        cells = [set() for _ in range(nx * ny)]  # each tile is a set
        for i, a in enumerate(actors):
            x, y, w, h = (round(v) for v in a.pos() + a.size())
            for tx in range((x - 1) // tile, 1 + (x + w + 1) // tile):
                for ty in range((y - 1) // tile, 1 + (y + h + 1) // tile):
                    if 0 <= tx < nx and 0 <= ty < ny:
                        # add actor `a` to the tile @ (tx, ty)
                        cells[ty * nx + tx].add(i)
        for i, a in enumerate(actors):
            neighs = set()
            x, y, w, h = (round(v) for v in a.pos() + a.size())
            for tx in range((x - 1) // tile, 1 + (x + w + 1) // tile):
                for ty in range((y - 1) // tile, 1 + (y + h + 1) // tile):
                    if 0 <= tx < nx and 0 <= ty < ny:
                        # all actors sharing some tile with `a`
                        neighs |= cells[ty * nx + tx]
            colls = [actors[j] for j in sorted(neighs, reverse=True)
                     if i != j and check_collision(a, actors[j])]
            self._collisions.append(colls)

    def collisions(self) -> list[Actor]:
        """Get list of actors colliding with current actor
        """
        t, colls = self._turn, self._collisions
        return colls[t] if 0 <= t < len(colls) else []

    def actors(self) -> list:
        """Return a copy of the list of actors.
        """
        return list(self._actors)

    def view_size(self) -> Point:
        return (self._w_view, self._h_view)

    def size(self) -> Point:
        """Return the size (w, h) of the arena.
        """
        return (self._w, self._h)

    def count(self) -> int:
        """Return the total count of ticks (or frames).
        """
        return self._count

    def current_keys(self) -> list[str]:
        """Return the currently pressed keys.
        """
        return self._curr_keys

    def previous_keys(self) -> list[str]:
        """Return the keys pressed at last tick.
        """
        return self._prev_keys
