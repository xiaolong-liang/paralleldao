
class BaseSystem(object):
    def __init__(self, states, governance):
        self.states = states
        self.governance = governance

    def update(self):
        pass

class DoraFutarchySystem(BaseSystem):
    def __init__(self):
        self.proposals = {}
        self.threshold = 5
        self.holds = {}
        self.proposal_holds = {}
        self.fees_rate = 0.1
        self.holds[0] = 0
        self.finished_proposal = []
        self.activate_proposal = []
        self.stack_lower_limit = 0.1

    def step(self):
        for proposal in self.proposals.values():
            if proposal.time >= self.threshold:
                self.proess_result(proposal._id)
                self.activate_proposal.remove(proposal._id)
                self.finished_proposal.append(proposal._id)
            else:
                proposal.time += 1
        
    def proess_result(self, proposal_id):
        if not proposal_id in self.proposal_holds.keys():
            raise Exception("unkown proposal")

        yes_sum = sum(self.proposal_holds[proposal_id]['yes'].values())
        no_sum = sum(self.proposal_holds[proposal_id]['no'].values())
        if yes_sum > no_sum:
            self.proposals[proposal_id].passed = 1
            yes_agents = self.proposal_holds[proposal_id]['yes']
            for key, value in yes_agents.items():
                self.holds[key] += no_sum * value/yes_sum
                self.holds[proposal_id] -= no_sum * value/yes_sum

        elif yes_sum < no_sum:
            self.proposals[proposal_id].passed = 0
            no_agents = self.proposal_holds[proposal_id]['no']
            for key, value in no_agents.items():
                self.holds[key] += yes_sum * value/no_sum
                self.holds[proposal_id] -= yes_sum * value/no_sum

        else:
            self.proposals[proposal_id].passed = 2
            yes_agents = self.proposal_holds[proposal_id]['yes']
            for key, value in yes_agents:
                self.holds[key] += value
                self.holds[proposal_id] -= value

            no_agents = self.proposal_holds[proposal_id]['no']
            for key, value in no_agents:
                self.holds[key] += value
                self.holds[proposal_id] -= value
        return

    def proposal(self, proposal):
        self.proposals[proposal._id] = proposal
        self.proposal_holds[proposal._id] = {
            'yes': {},
            'no': {}
        }
        self.holds[proposal._id] = 0
        self.activate_proposal.append(proposal._id)

    def add_agent(self, tokens, _id):
        self.holds[_id] = tokens

    def stack(self, token, agent_id, proposal_id, vote):
        has_token = self.holds.get(agent_id)
        if not has_token or has_token < token + token*self.fees_rate  or token < self.stack_lower_limit:
            return 0
        else:
            self.holds[agent_id] -= token + token*self.fees_rate
            self.proposal_holds[proposal_id][vote][agent_id] = token + self.proposal_holds[proposal_id][vote].get(agent_id, 0)
            self.holds[0] += token*self.fees_rate
            self.holds[proposal_id] += token
            return 1

    def get_activate_proposals(self):
        result = [self.proposals[_id] for _id in self.activate_proposal]
        return result

    def get_my_token(self, agent_id):
        return self.holds[agent_id]

    def is_voted(self, agent_id, proposal_id):
        if agent_id in self.proposal_holds[proposal_id]['yes'].keys() or agent_id in self.proposal_holds[proposal_id]['no'].keys():
            return True
        else:
            return False
