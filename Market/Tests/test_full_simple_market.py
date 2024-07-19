from Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Book.orderBook import OrderBook
from Book.orderBook import OrderTree
import matplotlib.pyplot as plt
import plotly.graph_objects as pltly


def test_book():
    agent_list = []

    ids = 1
    for i in range(50):
        fund_agent = Fundamentalist(ids, 100000)
        spec_agent = Speculator(ids+1, 100000)
        ids += 2
        fund_agent.set_shares(1)
        spec_agent.set_shares(1)
        agent_list.append(fund_agent)
        agent_list.append(spec_agent)
    
    LOB = OrderBook()

#DOWNWARDS PRESSURE MARKET PRICE TEST
    # for i in range(75,130):
    #     if(i in range(90,110)):
    #         order = {'type': 'limit',
    #                 'side': 'bid',
    #                 'qty': 1,
    #                 'price': i,
    #                 'agentID': 0,
    #                 'tid': 0}
    #         LOB.processOrder(order,False,False)
    #     if(i in range(115,130)):
    #         order = {'type': 'limit',
    #             'side': 'ask',
    #             'qty': 1,
    #             'price': i,
    #             'agentID': 0,
    #             'tid': 0}
    #         LOB.processOrder(order,False,False)
    #     else:
    #         pass

#UPWARDS PRESSURE MARKET PRICE TEST
    for i in range(75,115):
        if(i in range(75,80)):
            order = {'type': 'limit',
                    'side': 'bid',
                    'qty': 1,
                    'price': i,
                    'agentID': 0,
                    'tid': 0}
            LOB.processOrder(order,False,False)
        if(i in range(90,115)):
            order = {'type': 'limit',
                'side': 'ask',
                'qty': 1,
                'price': i,
                'agentID': 0,
                'tid': 0}
            LOB.processOrder(order,False,False)
        else:
            pass

    
    trades = 0
    x = []
    y = []
    for k in range(3):
        for i in range(len(agent_list)):
            time = LOB.get_time()
            if(LOB.get_market_price() != None):

                '''Decide how to determine market price
                by using the bestAsk/bestBid() as market price the result is more in-line with expectation
                when market price is the midpoint it stacking occurs between the agents so the price never moves
                and market price goes stagnant'''

                '''To assure market liquidity we will be simulating the market price not as them paying the market price itself but paying an additional premium
                in this case we will enact it as 5% of the market price as additional cost 
                When bidding this means and increase of 5%'''
                market_price = LOB.get_market_price() / 1000
                # market_price = LOB.getBestAsk() / 1000
                order = agent_list[i].trade(LOB.get_trend(), market_price, time)
                if(type(order) == dict):
                    print(order)
                    # print(LOB)
                    # print(LOB.get_trend())
                    LOB.processOrder(order, False, False)
                    x.append(time)
                    y.append(market_price)
                    if(len(LOB.get_trades()) > trades):
                        trades += 1
    print(LOB)
    # plt.plot(x,y)
    # plt.show()

    fig = pltly.Figure()
    fig.add_trace(pltly.Scatter(x=x, y=y, mode='lines', name='Line'))
    fig.update_layout(title='Market Price vs Time', xaxis_title='Time', yaxis_title='Market Price')
    fig.show()
    
if __name__ == '__main__':
    test_book()