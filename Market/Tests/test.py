from Market.Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Book.orderBook import OrderBook
import random 
import numpy as np

def test_book():
    fund_agent_list = []
    spec_agent_list = []

    ids = 1
    for i in range(100):
        inst_fund_agent = Fundamentalist(ids, 100000)
        ids += 1
        #inst_spec_agent = Speculator(ids+1, 100000)

        inst_fund_agent.set_shares(1)
        # ids += 2
        fund_agent_list.append(inst_fund_agent)
    
    bids = []
    asks = []
    market_prices = []
    LOB = OrderBook()

 #####Instantiate Initial Bids and Asks in Order Book ########
    for i in range(85,115):
        if(i in range(85,94)):
            order = {'type': 'limit',
                    'side': 'bid',
                    'qty': 1,
                    'price': i,
                    'agentID': 0,
                    'tid': 0}
            LOB.processOrder(order,False,False)
        if(i in range(105,115)):
            order = {'type': 'limit',
                'side': 'ask',
                'qty': 1,
                'price': i,
                'agentID': 0,
                'tid': 0}
            LOB.processOrder(order,False,False)
        else:
            pass

    highest = 0
    lowest = 0
    high_count = 0
    low_count = 0
    total_count = 0 

    for k in range(1):
        # bid = 0
        # ask = 0
        ''' random shuffle'''
        #random.shuffle(fund_agent_list)
        for i in range(len(fund_agent_list)):
            time = LOB.get_time()
            market_price = LOB.get_market_price() / 1000
            
            order = fund_agent_list[i].trade(market_price, time)
            #spec_order = spec_agent_list[i].trade(market_price)
##########################################################################################
            # print(LOB.get_last_6_prices())
            total_count += 1
            volatility = LOB.get_volatility()
            if(volatility > highest):
                highest = volatility
            elif(volatility < lowest):
                lowest = volatility
            elif(volatility >= 0.5):
                high_count += 1
            elif(volatility <= -0.5):
                low_count += 1
            market_prices.append(LOB.get_market_price())
#############################################################################################
            if(type(order) == dict):
                LOB.processOrder(order, False, False)
        #         if(order['side'] == 'bid'):
        #             bid += 1
        #         if(order['side'] == 'ask'):
        #             ask += 1
        # bids.append(bid)
        # asks.append(ask)

    print(LOB.get_trades())
    print(len(LOB.get_trades()))
        #fund_agent_list.pop(-1)                        
    
    # print(LOB.__str__())

    # print("Average Market Price: " + str(sum(market_prices)/len(market_prices)))
    # print("Average Bids: " + str(sum(bids)/len(bids)))
    # print("Average Asks: " + str(sum(asks)/len(asks)))
    # print("Highest volatility: " + str(highest))
    # print("Lowest volatility: " +str(lowest))
    # print("Volatility > 0.5%: " + str(high_count/total_count))
    # print("Volatility < -0.5%: " +str(low_count/total_count))

if __name__ == '__main__':
    test_book()