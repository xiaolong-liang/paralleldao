from .agent import SpatialAgent
class AgentFactory(object):
    
    @classmethod
    def gen_agent(tx, _type, number):
        result = []
        if _type == 'spatial':
            
            pass