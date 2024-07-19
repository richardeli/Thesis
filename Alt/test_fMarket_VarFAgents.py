from Market.Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Book.orderBook import OrderBook
from Book.orderBook import OrderTree
import plotly.graph_objects as pltly
import plotly.subplots as subplots

def test_book():
    figures = []

    ## Initial Instantiation
    ''' Max fund agent means max num of agents 
    100 max fund means 100 max speculators'''
    agent_list = []
    ids = 1
    #Used for l range for loop
    max_fund_agents = 100
    decrement_fund_agent = -10
    stop_val = -10

    for i in range(max_fund_agents):
        fund_agent = Fundamentalist(ids, 100000)
        spec_agent = Speculator(ids+1, 100000)
        ids += 2
        fund_agent.set_shares(1)
        spec_agent.set_shares(1)
        agent_list.append(fund_agent)
        agent_list.append(spec_agent)

    #Decrement by "decrement_fund_agent" so i.e. 100 first round next round will be 90 fundamentalists
    for l in range(max_fund_agents, stop_val, decrement_fund_agent):
        if l < max_fund_agents:
            num_remove = -(decrement_fund_agent)
            for agent in agent_list:
                if(num_remove > 0):
                    if isinstance(agent, Fundamentalist):
                        agent_list.remove(agent)
                        num_remove -= 1
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

        for k in range(1):
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
                        # print(order)
                        LOB.processOrder(order, False, False)
                        x.append(time)
                        y.append(market_price)
                        if(len(LOB.get_trades()) > trades):
                            trades += 1
        # print(LOB)
        fig = pltly.Figure()
        fig.add_trace(pltly.Scatter(x=x, y=y, mode='lines', name='Line'))
        fig.update_layout(title='Fundamentalist Agents: {l}', xaxis_title='Time', yaxis_title='Market Price')
        figures.append(fig)

    combined_fig = subplots.make_subplots(rows=(len(figures) // 3) + 1, cols=min(len(figures), 3), subplot_titles=[f'Fundamentalist Agents: {int(max_fund_agents - (i * -(decrement_fund_agent)))}' for i in range(len(figures))])

    for i, fig in enumerate(figures):
        row = (i // 3) + 1
        col = (i % 3) + 1
        combined_fig.add_trace(fig.data[0], row=row, col=col)

    combined_fig.update_layout(title='Combined Plot')
    combined_fig.show()

if __name__ == '__main__':
    test_book()