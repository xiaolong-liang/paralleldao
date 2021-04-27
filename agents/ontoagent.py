from owlready2 import get_ontology, default_world, sync_reasoner_pellet, World, set_datatype_iri
import os
from settings import BASE_DIR
from mesa import Agent, Model
import random

agent_base = os.path.join(BASE_DIR, 'resource', 'zlagent.owl')
set_datatype_iri(float, "http://www.w3.org/2001/XMLSchema#float")


class OntoAgent(Agent):
    def __init__(self, kb_path, unique_id: int, model: Model, market, system, pos, wealth=10, token=10, strategy=1) -> None:
        super().__init__(unique_id, model)
        self.kb_path = kb_path
        if not self.kb_path:
            self.kb_path = agent_base
        self.world = World()
        self.onto = self.world.get_ontology(self.kb_path)
        self.onto.load()
        self.unique_id = unique_id
        self.model = model
        self.market = market
        self.system = system
        self.pos = pos
        self.wealth = wealth
        self.token = token
        self.strategy = strategy
        self.yes_token = 0
        self.no_token = 0
        self.voted = False

        self.init_myself()

    def set_proposal(self, proposal_id, expect):
        """init the proposal knowlege in one proposal simulation
        """
        self.onto.proposal1.proposalId = proposal_id
        self.onto.proposal1.myExpectYes = float(expect)
        self.onto.proposal1.myExpectNo = float(1 - expect)
        self.onto.mySelf.currentProposal = self.onto.proposal1

    def init_myself(self):
        self.onto.GNO.myBanlance = float(self.token)
        self.onto.mySelf.wealth = float(self.wealth)
        self.onto.spatialAddress.hasX = float(self.pos[0])
        self.onto.spatialAddress.hasY = float(self.pos[1])
        if self.strategy == 0:
            self.onto.mySelf.myStrategy = self.onto.onlyBuy
        else:
            self.onto.mySelf.myStrategy = self.onto.buyAndSell
        self.onto.marketSystem.hasFee = float(self.market.fee)

    def think(self):
        """reason in kb using predefined rulers
        reason process dont introduce any new individuals
        """
        try:
            with self.onto:
                sync_reasoner_pellet(self.world, infer_property_values=True,
                                     infer_data_property_values=True, debug=2)

        except Exception as e:
            print(e)
        self._replace_ready_property()

    def _replace_ready_property(self):
        # update goal
        individuals = self.onto.individuals()
        for individual in individuals:
            property_names = [
                property._name for property in individual.get_properties()]
            update_paris = []
            for property_name in property_names:
                if property_name.endswith('Ready'):
                    update_paris.append((property_name, property_name[:-5]))
            if update_paris:
                for property_ready, property in update_paris:
                    ready_value = eval('individual.' + property_ready)
                    now_value = eval('individual.' + property)
                    if not ready_value:
                        continue

                    if isinstance(ready_value, list):
                        individual.__dict__[property_ready] = []
                        if isinstance(now_value, list):
                            individual.__dict__[property] = ready_value
                        else:
                            individual.__dict__[property] = ready_value[0]
                    else:
                        individual.__dict__[property_ready] = None
                        if isinstance(now_value, list):
                            individual.__dict__[property] = [ready_value]
                        else:
                            individual.__dict__[property] = ready_value

    def observe(self):
        # print(self.onto.yesToken.expectBenefitReady)
        # print(self.onto.noToken.expectBenefitReady)
        # print(self.onto.mySelf.currentGoalReady)
        # print(self.onto.yesToken.expectBenefit)
        # print(self.onto.noToken.expectBenefit)
        # print(self.onto.mySelf.currentGoal)
        proposals = self.system.observe(self)
        if proposals:
            target = proposals[0]
        else:
            target = None

        if not target:
            self.onto.mySelf.currentProposal = None
            return
        yes_prices = self.market.calc_price(target._id, 1, 0)
        no_prices = self.market.calc_price(target._id, 0, 1)
        # yesToken  noToken is the condional token of proposal1
        self.onto.noToken.currentPrice = float(no_prices)
        self.onto.yesToken.currentPrice = float(yes_prices)
        self.onto.GNO.myBanlance = float(self.token)
        self.onto.mySelf.myWealth = float(self.wealth)

    def execute(self):

        def buy_yes_token(_id, amount):
            pay = self.market.calc_price(_id, amount, 0)
            if pay <= self.token:
                val = self.market.buy(_id, self.unique_id, 'yes_token', amount)
                self.yes_token += amount
                self.token -= val

        def buy_no_token(_id, amount):
            price = self.market.calc_price(_id, 0, amount)
            if price <= self.token:
                val = self.market.buy(_id, self.unique_id, 'no_token', amount)
                self.no_token += amount
                self.token -= val

        def sell_yes_token(_id, amount):
            if self.yes_token >= amount:
                val = self.market.sell(
                    _id, self.unique_id, 'yes_token', amount)
                self.yes_token -= amount
                self.token -= val

        def sell_no_token(_id, amount):
            if self.no_token >= amount:
                val = self.market.sell(_id, self.unique_id, 'no_token', amount)
                self.no_token -= amount
                self.token -= val

        def vote_yes(_id, amount=None):
            self.system.vote(self, _id, 'yes')
            self.voted = True

        def vote_no(_id, amount=None):
            self.system.vote(self, _id, 'no')
            self.voted = True

        plan = self.onto.myPlan
        actions = plan.hasAction
        while actions:
            action = actions.pop(0)
            token = action.targetToken

            if action._name == 'buyYesToken':
                proposal = token.yesTokenOf
                _id = proposal.proposalId
                amount = action.buyAmount
                _func = buy_yes_token
            elif action._name == 'sellYesToken':
                proposal = token.yesTokenOf
                _id = proposal.proposalId
                amount = action.sellAmount
                _func = sell_yes_token

            elif action._name == 'buyNoToken':
                proposal = token.noTokenOf
                _id = proposal.proposalId
                amount = action.buyAmount
                _func = buy_no_token

            elif action._name == 'sellNoToken':
                proposal = token.noTokenOf
                _id = proposal.proposalId
                amount = action.sellAmount
                _func = sell_no_token
            elif action.name == 'voteYes':
                proposal = action.targetProposal
                _id = proposal.proposalId
                amount = 1
                _func = vote_yes
            elif action.name == 'voteNo':
                proposal = action.targetProposal
                _id = proposal.proposalId
                amount = 1
                _func = vote_no
            else:
                continue
            _func(_id, amount)
            self.wealth = self.token + self.no_token * \
                self.market.calc_price(
                    _id, 0, 1) + self.yes_token * self.market.calc_price(_id, 1, 0)

    def step(self):
        print("agent {} started to thinking".format(self.unique_id))
        self.observe()
        self.think()
        self.execute()


if __name__ == '__main__':
    agent = OntoAgent(agent_base, 0, None, None, None, [0, 0])
    agent.step()
    # agent2.step()
