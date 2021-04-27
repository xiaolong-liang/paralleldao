from enum import Enum
class State(Enum):
    Init = 1
    Pass = 2
    Failed = 3
    pass

class Proposal(object):
    def __init__(self, _meta, _id, pos):
        self._meta = _meta
        self.state = 1
        self._id = _id
        self.time = 0
        self.passed = -1
        self.pos = pos

    def update(self, state):
        self.state = state



class FutarchyProposal(Proposal):
    def __init__(self, _meta, _id, pos, b_number):
        super().__init__(_meta, _id, pos)
        self.historys = {'1': {'yes_token':0, 'no_token': 0}}
        self.prices = {
            'Yes': 1,
            'No': 1
        }

        self.yes_token = 0
        self.no_token = 0
        self.b_number = b_number