from Market.Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Book.orderBook import OrderBook
import random 
import numpy as np
import math

def test_book():
    LOB = OrderBook()

 #####Instantiate Initial Bids and Asks in Order Book ########
    for i in range(1,20):
        if(i in range(1,10)):
            order = {'type': 'limit',
                    'side': 'bid',
                    'qty': 1,
                    'price': i,
                    'agentID': 0,
                    'tid': 0}
            LOB.processOrder(order,False,False)
        elif(i in range(11,20)):
            order = {'type': 'limit',
                'side': 'ask',
                'qty': 1,
                'price': i,
                'agentID': 0,
                'tid': 0}
            LOB.processOrder(order,False,False)
        else:
            pass

    for i in range (1,10):
        bid_p = random.randint(5, 15)
        ask_p = random.randint(1, 13)
        order = {'type': 'limit',
                'side': 'bid',
                'qty': 1,
                'price': bid_p,
                'agentID': 0,
                'tid': 0}
        order = {'type': 'limit',
                'side': 'ask',
                'qty': 1,
                'price': ask_p,
                'agentID': 0,
                'tid': 0}
        LOB.processOrder(order, False, False)

        print("Bid price: " + str(bid_p))
        print("Ask price:" + str(ask_p))
        print("Trend:" + str(LOB.get_trend()))
        print(LOB.get_last_6_prices())
    
    print(LOB.__str__())
    #print(LOB.get_last_6_prices())

if __name__ == '__main__':
    test_book()