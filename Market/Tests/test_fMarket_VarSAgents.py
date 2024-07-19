from Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Book.orderBook import OrderBook
from Book.orderBook import OrderTree
import plotly.graph_objects as pltly
from plotly.subplots import make_subplots


def test_book():
    figures = []

    ## Initial Instantiation
    ''' Max fund agent means max num of agents 
    100 max fund means 100 max speculators'''
    agent_list = []
    ids = 1
    num_one_type_init_agent = 25


    for i in range(num_one_type_init_agent):
        fund_agent = Fundamentalist(ids, 100000)
        spec_agent = Speculator(ids+1, 100000)
        ids += 2
        fund_agent.set_shares(1)
        spec_agent.set_shares(1)
        agent_list.append(fund_agent)
        agent_list.append(spec_agent)            
    
    LOB = OrderBook()

    #DOWNWARDS PRESSURE MARKET PRICE TEST
    # for i in range(1,200):
    #     if(i in range(1,110)):
    #         order = {'type': 'limit',
    #                 'side': 'bid',
    #                 'qty': 1,
    #                 'price': i,
    #                 'agentID': 0,
    #                 'tid': 0}
    #         LOB.processOrder(order,False,False)
    #     if(i in range(115,200)):
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
    for i in range(1,200):
        if(i in range(1,80)):
            order = {'type': 'limit',
                    'side': 'bid',
                    'qty': 1,
                    'price': i,
                    'agentID': 0,
                    'tid': 0}
            LOB.processOrder(order,False,False)
        if(i in range(90,200)):
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
    order_num = 0
    x = []
    y_market_price = []
    y_trend = []
    y_agent_type = []

    for k in range(10):
        if k > 1:
            max_fund_agents = 20
            decrement_fund_agent = -10
            stop_val = -10
            for l in range(max_fund_agents, stop_val, decrement_fund_agent):
                if l < max_fund_agents:
                    num_remove = -(decrement_fund_agent)
                    for agent in agent_list:
                        if(num_remove > 0):
                            if isinstance(agent, Fundamentalist):
                                agent_list.remove(agent)
                                num_remove -= 1
                                
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
                order = agent_list[i].trade(LOB.get_trend(), market_price, time)
                if(type(order) == dict):
                    LOB.processOrder(order, False, False)
                    if(len(LOB.get_trades()) > trades):
                        trades += 1
                x.append(order_num)
                order_num += 1
                y_market_price.append(market_price)
                y_trend.append(LOB.get_trend())

                speculator_proportion = round((num_one_type_init_agent + k * 50) / (num_one_type_init_agent*2 + k * 50),4) * 100
                agent_type = agent_list[i].get_agentType()
                y_agent_type.append([agent_type, str(speculator_proportion) + "%"])
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=('Market Price', 'Trend'))
    fig.add_trace(pltly.Scatter(x=x, y=y_market_price, mode='lines', name='Market Price', line=dict(color='blue'), hovertext=y_agent_type), row=1, col=1)
    fig.add_trace(pltly.Scatter(x=x, y=y_trend, mode='lines', name='Trend', line=dict(color='red'), hovertext=y_agent_type), row=2, col=1)
    fig.update_layout(height=600, width=800, title_text="Market Price and Trend vs. Time", showlegend=False)
    fig.update_xaxes(title_text='Time', row=2, col=1) 
    fig.show()


if __name__ == '__main__':
    test_book()