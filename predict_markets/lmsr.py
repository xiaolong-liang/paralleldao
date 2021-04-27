from . import PredictMarket
import math
from enum import Enum


class TokenType(Enum):
    yes_token = 'yes_token'
    no_token = 'no_token'


class LMSR(PredictMarket):
    def __init__(self, fee=0.02) -> None:
        super().__init__()
        self.proposal_map = {}
        self.fee = fee

    def submit(self, agent, proposal):
        self.proposals.append(proposal)
        self.proposal_map[proposal._id] = proposal

    def buy(self, proposal_id, agent, token_type, amount):
        proposal = self.proposal_map[proposal_id]
        token_type = TokenType(token_type)
        val = 0
        if token_type == TokenType.yes_token:
            val = self.calc_price(proposal._id, amount, 0)
            proposal.yes_token += amount
        elif token_type == TokenType.no_token:
            val = self.calc_price(proposal._id, 0, amount)
            proposal.no_token += amount
        else:
            raise Exception('unknown token type')
        return val

    def sell(self, proposal_id, agent, token_type, amount):
        proposal = self.proposal_map[proposal_id]
        token_type = TokenType(token_type)
        val = 0
        if token_type == TokenType.yes_token:
            if amount > proposal.yes_token:
                return 0
            val = self.calc_price(proposal._id, -amount, 0)
            proposal.yes_token -= amount
        elif token_type == TokenType.no_token:
            if amount > proposal.no_token:
                return 0
            val = self.calc_price(proposal._id, -amount, 0)
            proposal.no_token -= amount
        else:
            raise Exception('unknown token type')
        return val

    def calc_price(self, proposal_id, yes_token, no_token):
        """compute the price of current proposal
        """
        proposal = self.proposal_map[proposal_id]
        b = proposal.b_number
        p_w = proposal.yes_token
        p_l = proposal.no_token
        if proposal.state == 2:
            return yes_token
        elif proposal.state == 3:
            return no_token

        c_n = b * math.log(math.exp((p_w + yes_token)/b) +
                           math.exp((p_l + no_token)/b))
        c_p = b * math.log(math.exp(p_w/b) + math.exp(p_l/b))
        val = c_n - c_p
        val = round(val, 2)
        return val
