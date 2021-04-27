import sys
sys.path.append(".")
from predict_markets.lmsr import LMSR
from proposal import FutarchyProposal

def test_calc():
    proposal = FutarchyProposal("", 1, [0,1],300)
    lmsr = LMSR()
    lmsr.submit('', proposal)
    print(lmsr.calc_price(1, 1, 0))
    lmsr.buy(1, 0, 'yes_token', 1)
    lmsr.buy(1, 0, 'yes_token', 1)
    print(lmsr.calc_price(1,0,1))
    assert lmsr.calc_price(1, 1, 0) == 1