from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
from mesa.space import Grid
from psystems.psystem import DoraFutarchySystem
from agents.agent import SpatialAgent
import numpy as np
from proposal import  Proposal

class SimpleModel(object):
    """
    """
    def __init__(self) -> None:
        """
        """
        proposal = Proposal({}, '123', [1,1])
        self.schedule = BaseScheduler(self)
        self.system = DoraFutarchySystem()
        self.system.proposal(proposal)
        self.grid = Grid(10,10, torus=False)

        for pos in [[0,1], [1,0], [1,1], [0,0]]:
            agent = SpatialAgent(pos, self, self.system, None, None, "{}_{}".format(pos[0], pos[1]))
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