from enum import Enum
class State(Enum):
    Init = 1
    Pass = 2
    Failed = 3
    pass

class Proposal(object):
    def __init__(self, _meta, _id, pos):
        self._meta = _meta
        self.state = State(1)
        self._id = _id
        self.time = 0
        self.passed = -1
        self.pos = pos

    def update(self, state):
        self.state = state