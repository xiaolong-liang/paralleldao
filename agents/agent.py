import math
from mesa import Agent, Model
import random

# class Agent(object):
#     def __init__(self, _id, position, states):
#         self._id = _id
#         self.position = position
#         self.states = states


class SpatialAgent(Agent):
    """ 
    A Spatial Vote agent
    agent with x,y represents it's opinion
    """

    def __init__(self, pos, model, system, forum, knowlege, _id=None):
        """
        create a new voter
        Args:
            pos: the opinon position
            model: the model 
            system: the simluated system
            forum: social concact net
            knowlege: knowlege represent of this agent
            _id: id
        each time, the agent will focus on one proposal
        """
        self.pos = pos
        self.model = model
        self.system = system
        self.forum = forum
        self._id = _id
        self.unique_id = _id
        self.knowlege = knowlege
        self.like_threshold = 0.7
        self.hate_threshold = 1
        self.condition = 'Unknown'

    def observe(self, system):
        # infos = system.observe(self)
        proposals = system.get_activate_proposals()
        favorite_proposal = None
        shortest_distance = 10000
        for proposal in proposals:
            if system.is_voted(self._id, proposal._id):
                continue
            else:
                dist = self.likes(proposal)
                if dist < shortest_distance:
                    shortest_distance = dist
                    favorite_proposal = proposal
        return favorite_proposal, dist

    def likes(self, proposal):
        x = self.pos
        y = proposal.pos
        sum_result = sum([math.pow(i-j, 2)for i, j in zip(x, y)])
        dist = math.sqrt(sum_result)
        return dist

    def think(self):
        """this step, agent try to reason his belief, intent
        """
        pass

    def check_intent(self):
        pass

    def update_intent(self):
        pass

    def check_plan(self):
        pass

    def execute_plan(self):
        """
        """
        def vote(amount):
            pass
        pass

    def step(self):
        print('voted')
        proposal, dist = self.observe(self.system)
        if proposal and dist < self.like_threshold:
            self.system.stack(0.1, self._id, proposal._id, 'yes')
            self.condition = 'Yes'
        elif proposal and dist > self.hate_threshold:
            self.system.stack(0.1, self._id, proposal._id, 'yes')
            self.condition = 'No'
        else:
            self.condition = 'Unknown'

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]


class FutarchyRandomAgent(Agent):
    def __init__(self, unique_id: int, model: Model, market, system, pos) -> None:
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.model = model
        self.market = market
        self.system = system
        self.token = 10
        self.no_token = 0
        self.yes_token = 0
        self.pos = pos
        self.wealth = self.token
        self.voted = False

    def step(self) -> None:
        proposals = self.system.observe(self)
        if proposals:
            target = proposals[0]
        else:
            return
        dice = random.random()
        val = 0
        if dice < 0.25:
            price = self.market.calc_price(target._id, 1, 0)
            if price <= self.token:
                val = self.market.buy(
                    target._id, self.unique_id, 'yes_token', 1)
                self.yes_token += 1
                self.system.vote(self, target._id, 'yes')
                self.voted = True

        elif dice > 0.25 and dice < 0.5:
            if self.yes_token >= 1:
                val = self.market.sell(
                    target._id, self.unique_id, 'yes_token', 1)
                self.yes_token -= 1
        elif dice > 0.5 and dice < 0.75:

            if self.no_token >= 1:
                val = self.market.sell(
                    target._id, self.unique_id, 'no_token', 1)
                self.no_token -= 1
        elif dice > 0.75:
            price = self.market.calc_price(target._id, 0, 1)
            if price <= self.token:
                val = self.market.buy(
                    target._id, self.unique_id, 'no_token', 1)
                self.no_token += 1
            self.system.vote(self, target._id, 'no')
            self.voted = True

        self.token -= val
        self.wealth = self.token + self.no_token * self.market.calc_price(
            target._id, 0, 1) + self.yes_token * self.market.calc_price(target._id, 1, 0)
        # self.wealth = self.token + self.no_token * self.market.calc_price(target._id, 0, 1)
        # self.wealth = self.token + self.yes_token * self.market.calc_price(target._id, 1, 0)
        return super().step()
