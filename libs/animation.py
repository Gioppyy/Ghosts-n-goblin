class Animation:
    def __init__(self, frames, speed=1, loop=True, on_complete=None, on_update=None):
        self._frames = frames
        self._speed = speed
        self._loop = loop
        self._on_complete = on_complete
        self._on_update = on_update
        self._current_frame = 0
        self._tick = 0
        self._active = False
        self._completed = False

    def start(self):
        self._active = True
        self._completed = False
        self._current_frame = 0
        self._tick = 0
        return self._frames[self._current_frame]

    def stop(self):
        self._active = False

    def update(self):
        if not self._active or self._completed:
            return

        self._tick += 1
        if self._tick >= self._speed:
            self._tick = 0
            self._current_frame += 1
            if self._on_update:
                self._on_update()

            if self._current_frame >= len(self._frames):
                if self._loop:
                    self._current_frame = 0
                else:
                    self._current_frame = len(self._frames) - 1
                    self._completed = True
                    if self._on_complete:
                        self._on_complete()
        return self._frames[self._current_frame]

    def set_on_complete(self, on_complete):
        self._on_complete = on_complete

    def frames(self):
        return self._frames

    def is_active(self):
        return self._active and not self._completed
