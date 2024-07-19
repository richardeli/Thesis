from Market.Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Book.orderBook import OrderBook
from Book.orderBook import OrderTree

def test_book():

    agent_list = []

    ids = 1
    for i in range(30):
        spec_agent = Speculator(ids+1, 100000)
        ids += 1
        spec_agent.set_shares(1)
        agent_list.append(spec_agent)

        # fund_agent = Fundamentalist(ids, 100000)
        # spec_agent = Speculator(ids+1, 100000)

        # ids += 2
        # fund_agent.set_shares(1)
        # spec_agent.set_shares(1)

        # agent_list.append(fund_agent)
        # agent_list.append(spec_agent)
    
    LOB = OrderBook()

    for i in range(85,115):
        if(i in range(85,94)):
            order = {'type': 'limit',
                    'side': 'bid',
                    'qty': 1,
                    'price': i,
                    'agentID': 0,
                    'tid': 0}
            LOB.processOrder(order,False,False)
        if(i in range(100,115)):
            order = {'type': 'limit',
                'side': 'ask',
                'qty': 1,
                'price': i,
                'agentID': 0,
                'tid': 0}
            LOB.processOrder(order,False,False)
        else:
            pass

    for k in range(1):
        for i in range(100,107):
            order = {'type': 'limit',
                    'side': 'bid',
                    'qty': 1,
                    'price': i,
                    'agentID': 0,
                    'tid': 0}
            LOB.processOrder(order,False,False)

        for i in range(len(agent_list)):
            time = LOB.get_time()
            market_price = LOB.get_market_price() / 1000
            
            #order = agent_list[i].trade(market_price, time)
            order = agent_list[i].trade(LOB.get_trend(), market_price, time)
                        
            if(type(order) == dict):
                LOB.processOrder(order, False, False)

        trades = LOB.get_trades()
        for i in range(len(trades)):
            settle = trades[i]
            if(settle['party1'][1] == 'bid'):
                party1_agentID = settle['party1'][0]
                party2_agentID = settle['party2'][0]

                #ls get from stored list of agents
                #agent1 fund_agent_list[party1_agentID]
                #agent2 fund_agent_list[party2_agentID]
                #agent1.settle_trade()
                #agent2.settle_trader()

            elif(settle['party1'][0] == 'ask'):
                party1_agentID = settle['party1'][0]
                party2_agentID = settle['party2'][0]

                #ls get from stored list of agents
                #agent1 fund_agent_list[party1_agentID]
                #agent2 fund_agent_list[party2_agentID]
                #agent1.settle_trade()
                #agent2.settle_trader()  
            else:
                pass

    #print(LOB.get_trades())
    #print(len(LOB.get_trades()))
    
    #print(LOB.__str__())

if __name__ == '__main__':
    test_book()