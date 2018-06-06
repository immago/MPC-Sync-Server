from enum import IntEnum
import json

class State(IntEnum):
    Closed = -1
    Stoped = 0
    Paused = 1
    Playing = 2


class Data:
    def __init__(self, file, duration, position, state):
        self.file = file
        self.duration = duration
        self.position = position
        self.state = state
        
    def jsonValue(self):
        return json.dumps({'file': self.file, 'duration': self.duration, 'position': self.position, 'state': self.state})

class Callback:
    def __init__(self, identifer, function):
        self.identifer = identifer
        self.function = function