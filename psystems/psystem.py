
from proposal import Proposal


class BaseSystem(object):
    def __init__(self, states, governance):
        self.states = states
        self.governance = governance

    def update(self):
        pass


class DoraFutarchySystem(BaseSystem):
    """this system is created referenced to the dora voting experiment, but it didn't finished, dont use it
    """

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
        if not has_token or has_token < token + token*self.fees_rate or token < self.stack_lower_limit:
            return 0
        else:
            self.holds[agent_id] -= token + token*self.fees_rate
            self.proposal_holds[proposal_id][vote][agent_id] = token + \
                self.proposal_holds[proposal_id][vote].get(agent_id, 0)
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


class FutarchySystem(BaseSystem):
    """the origin futarchy system
    """

    def __init__(self, forum=None):
        self.failed_proposals = []
        self.activate_proposals = []
        self.passed_proposals = []
        self.forum = forum

    def update(self):
        """
        update the system time to t + 1
        """
        pass

    def observe(self, agent_id):
        """
        observe from the agent
        """
        pass

    def propose(self, proposal, agent):
        pass


class SimpleFutarchySystem(FutarchySystem):
    def __init__(self, forum=None, predict_market=None, duration=14):
        super().__init__(forum)
        self.predict_market = predict_market
        self.orders = []
        self.time_stick = 0
        self.day = 0
        self.duration = duration
        # self.vote_actions = {
        #     'yes': [],
        #     'no': []
        # }
        self.vote_actions = {}
        self.voted_agents = set()

    def update(self):
        self.time_stick += 1

    def propose(self, proposal):
        proposal.time = self.day
        self.activate_proposals.append(proposal)
        self.predict_market.submit(-1, proposal)
        self.vote_actions[proposal._id] = {
            'yes': [],
            'no': []
        }

    def vote(self, agent, proposal_id, vote_type):
        if agent.unique_id in self.voted_agents or agent.token < 1:
            return
        vote_action = self.vote_actions[proposal_id]
        if vote_type == 'yes':
            vote_action['yes'].append((agent.unique_id, agent.token))
        elif vote_type == 'no':
            vote_action['yes'].append((agent.unique_id, agent.token))
        self.voted_agents.add(agent.unique_id)

    def step(self):
        # self.time_stick += 1
        # self.day = int(self.time_stick/24)
        self.day += 1
        remove_list = []
        for proposal in self.activate_proposals:
            if self.day - proposal.time >= self.duration:
                # self.activate_proposals.remove(proposal)
                remove_list.append(proposal)
                vote_action = self.vote_actions[proposal._id]

                yes_amount = sum(x[1] for x in vote_action['yes'])
                no_amount = sum(x[1] for x in vote_action['no'])

                if yes_amount > no_amount:
                    proposal.state = 2
                    self.passed_proposals.append(proposal)
                else:
                    proposal.state = 3
                    self.failed_proposals.append(proposal)

        for proposal in remove_list:
            self.activate_proposals.remove(proposal)

    def observe(self, agent):
        return self.activate_proposals
