class Animation:
    def __init__(self, frames, speed, loop=True):
        self.frames = frames
        self.speed = speed
        self.loop = loop
        self.tick = 0
        self.index = 0
        self.playing = False

    def start(self, frames=None, speed=None, loop=True):
        if frames is not None:
            self.frames = frames
        if speed is not None:
            self.speed = speed
            self.loop = loop
            self.tick = 0
            self.index = 0
            self.playing = True

    def stop(self):
        self.playing = False
        self.index = 0
        self.tick = 0

    def update(self):
        if not self.playing:
            return self.frames[self.index]

        self.tick += 1
        if self.tick >= self.speed:
            self.tick = 0
            self.index += 1

        if self.index >= len(self.frames):
            if self.loop:
                self.index = 0
            else:
                self.index = len(self.frames) - 1
                self.playing = False

        return self.frames[self.index]
