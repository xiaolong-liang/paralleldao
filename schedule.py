"""to be down
"""
class Scheduler(object):
    def __init__(self):
        self.agents = {}

    def setp(self):
        for agent in self.agents.values():
            agent.step()

    def add(self, agent):
        # self.agents.add(agent)
        self.agents[agent._id] = agent