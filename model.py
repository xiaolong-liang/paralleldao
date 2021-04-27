from mesa import Model
from mesa.time import BaseScheduler, RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import Grid
from psystems.psystem import DoraFutarchySystem, SimpleFutarchySystem
from agents.agent import SpatialAgent, FutarchyRandomAgent
from agents.ontoagent import OntoAgent
from predict_markets.lmsr import LMSR
import numpy as np
from proposal import Proposal, FutarchyProposal
import random


class SimpleModel(object):
    """
    """

    def __init__(self) -> None:
        """
        """
        proposal = Proposal({}, '123', [1, 1])
        self.schedule = RandomActivation(self)
        self.system = DoraFutarchySystem()
        self.system.proposal(proposal)
        self.grid = Grid(10, 10, torus=False)

        for pos in [[0, 1], [1, 0], [1, 1], [0, 0]]:
            agent = SpatialAgent(pos, self, self.system,
                                 None, None, "{}_{}".format(pos[0], pos[1]))
            self.grid.place_agent(agent, tuple(pos))
            self.schedule.add(agent)

        self.running = True
        self.datacollector = DataCollector(
            {
                "Yes": lambda m: self.count_type(m, "Yes"),
                "No": lambda m: self.count_type(m, "No"),
                "Unknown": lambda m: self.count_type(m, 'Unknown')
            }
        )
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        self.running = False

    @staticmethod
    def count_type(model, voter_condition):
        """

        """
        count = 0
        for voter in model.schedule.agents:
            if voter.condition == voter_condition:
                count += 1
        return count


class Furtarchy(Model):
    """
    """

    def __init__(self, b_number, agent_number, kinds=[5, 5, 20], fee=0.5) -> None:
        """
        """
        proposal = FutarchyProposal(None, 0, [], b_number)
        self.schedule = RandomActivation(self)
        self.market = LMSR(fee=fee)
        self.system = SimpleFutarchySystem(
            forum=None, predict_market=self.market)
        self.system.propose(proposal)
        self.grid = Grid(10, 10, torus=False)
        self.count = 0
        self.agent_numer = sum(kinds)
        for i in range(0, 10):
            for j in range(0, 10):
                if j + i*10 <= kinds[0]:
                    # agent = FutarchyRandomAgent(j+i*10, self, self.market, self.system, (i, j))
                    agent = OntoAgent(None, j+i*10, self,
                                      self.market, self.system, (i, j), strategy=0)
                    self.grid.place_agent(agent, (i, j))
                    self.schedule.add(agent)
                    agent.set_proposal(proposal._id, 0.6)
                elif j + i*10 <= kinds[0] + kinds[1]:
                    agent = OntoAgent(None, j+i*10, self,
                                      self.market, self.system, (i, j), strategy=1)
                    self.grid.place_agent(agent, (i, j))
                    self.schedule.add(agent)
                    agent.set_proposal(proposal._id, 0.6)

                elif j + i*10 <= kinds[0] + kinds[1] + kinds[2]:
                    agent = FutarchyRandomAgent(
                        j+i*10, self, self.market, self.system, (i, j))
                    self.grid.place_agent(agent, (i, j))
                    self.schedule.add(agent)
                else:
                    continue

        self.running = True
        self.datacollector = DataCollector(
            {
                "yes_token_price": lambda m: self.count_type(m, m.market, 'yes'),
                "no_token_price": lambda m: self.count_type(m, m.market, 'no')
            }
        )
        self.datacollector.collect(self)

        self.countcollector = DataCollector(
            {
                "yes_token": lambda m: self.count_token(m, 'yes'),
                "no_token": lambda m: self.count_token(m, 'no')
            }
        )
        self.countcollector.collect(self)

    def step(self):
        # self.schedule.agents
        # index = self.count % self.agent_numer
        index = random.randint(0, self.agent_numer - 1)
        current_agent = self.schedule.agents[index]
        current_agent.step()

        self.datacollector.collect(self)
        self.countcollector.collect(self)
        if self.count % (24*self.agent_numer) == 0 and self.count > 0:
            self.system.step()
        if self.count >= 15*24*self.agent_numer:
            self.running = False
        self.count += 1

    @staticmethod
    def count_type(model, market, voter_condition):
        """
        """
        if not model.system.activate_proposals:
            return 0
        proposal = model.system.activate_proposals[0]
        if voter_condition == 'yes':
            return market.calc_price(proposal._id, 1, 0)
            # val = proposal.yes_token
        else:
            return market.calc_price(proposal._id, 0, 1)
            # val = proposal.no_token
        return val

    @staticmethod
    def count_token(model, voter_condition):
        """

        """
        count = 0
        if voter_condition == 'yes':
            for voter in model.schedule.agents:
                count += voter.yes_token
        else:
            for voter in model.schedule.agents:
                count += voter.no_token
        return count
