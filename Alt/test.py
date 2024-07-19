from Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Book.orderBook import OrderBook
import random 

def test_book():
    fund_agent_list = []
    spec_agent_list = []

    LOB = OrderBook()

    ids = 1
    for i in range(100):
        inst_fund_agent = Fundamentalist(ids, 1000)
        inst_spec_agent = Speculator(ids+1, 1000)

#Randomly allocate share count for each agent
        inst_fund_agent.set_shares(random.randint(0,50))

        ids += 2
        fund_agent_list.append(inst_fund_agent)
        spec_agent_list.append(inst_spec_agent)

#Process Orders for Round Iteration number 1
    for i in range(len(fund_agent_list)):

        #market_price = LOB.get_market_price()
        market_price = 100
        time = LOB.get_time()

        order = fund_agent_list[i].trade(market_price, time)
        #spec_order = spec_agent_list[i].trade(market_price)
        
        if(type(order) == dict):
            LOB.processOrder(order, False, False)
            #LOB.processOrder(spec_order)

    print(LOB.get_asks())
    print('||||||')
    print(LOB.get_bids())
        
if __name__ == '__main__':
    test_book()