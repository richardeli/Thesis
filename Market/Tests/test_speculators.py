from Agents.speculator import Speculator
from Book.orderBook import OrderBook
from Book.orderBook import OrderTree
import numpy as np
import plotly.graph_objects as pltly


def test_book():

    agent_list = []

    ids = 1
    for i in range(50):
        spec_agent = Speculator(ids, 100000)
        ids += 1
        spec_agent.set_shares(1)
        agent_list.append(spec_agent)
    
    LOB = OrderBook()

    for i in range(85,115):
        if(i in range(80,94)):
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

    x = []
    y = []
    for k in range(1):
        if(k == 0):
            for i in range(95,87, -1):
                order = {'type': 'limit',
                        'side': 'ask',
                        'qty': 1,
                        'price': i,
                        'agentID': 0,
                        'tid': 0}
                LOB.processOrder(order,False,False)
            trades = LOB.get_trades()
        for i in range(len(agent_list)):
            time = LOB.get_time()
            if(LOB.get_market_price() != None):
                market_price = LOB.get_market_price() / 1000
                # print(market_price)
                # print(agent_list[i].get_agentID())
                # print(LOB.get_trend())
                order = agent_list[i].trade(LOB.get_trend(), market_price, time)
                if(type(order) == dict):
                    LOB.processOrder(order, False, False)
                    x.append(time)
                    y.append(market_price)

    fig = pltly.Figure()
    fig.add_trace(pltly.Scatter(x=x, y=y, mode='lines', name='Line'))
    fig.update_layout(title='Market Price vs Time', xaxis_title='Time', yaxis_title='Market Price')
    fig.show()

if __name__ == '__main__':
    test_book()