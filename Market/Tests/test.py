from Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Agents.moderator import Moderator
from Book.orderBook import OrderBook
from Book.orderBook import OrderTree
import plotly.graph_objects as pltly
from plotly.subplots import make_subplots
'''
TO DO - organise moderator for agentID 0 object
'''

def test_book():
    ## Initial Instantiation
    ''' Max fund agent means max num of agents 
    100 max fund means 100 max speculators'''
    agent_dict = {}
    moderator = Moderator()
    agent_dict[moderator.get_agentID()] = {
            "agent_object": moderator,
            "type": "Moderator"
    }

    ids = 1
    num_one_type_init_agent = 25
    for i in range(num_one_type_init_agent):
        fund_agent = Fundamentalist(ids, 100000)
        spec_agent = Speculator(ids + 1, 100000)
        ids += 2
        fund_agent.set_shares(1)
        spec_agent.set_shares(1)
        agent_dict[fund_agent.get_agentID()] = {
            "agent_object": fund_agent,
            "type": "Fundamentalist"
        }

        # Add Speculator agent to the dictionary
        agent_dict[spec_agent.get_agentID()] = {
            "agent_object": spec_agent,
            "type": "Speculator"
        }
    LOB = OrderBook()

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
            moderator.add_share(order['qty'])
        else:
            pass

    #DOWNWARDS PRESSURE MARKET PRICE TEST
    # for i in range(1,200):
    #     if(i in range(1,120)):
    #         order = {'type': 'limit',
    #                 'side': 'bid',
    #                 'qty': 1,
    #                 'price': i,
    #                 'agentID': 0,
    #                 'tid': 0}
    #         LOB.processOrder(order,False,False)
    #     if(i in range(130,200)):
    #         order = {'type': 'limit',
    #             'side': 'ask',
    #             'qty': 1,
    #             'price': i,
    #             'agentID': 0,
    #             'tid': 0}
    #         LOB.processOrder(order,False,False)
    #         moderator.add_share(order['qty'])
    #     else:
    #         pass

    trades = 0
    order_num = 0
    x = []
    y_market_price = []
    y_trend = []
    y_agent_type = []

    for k in range(50):
        if k > 1:
            max_fund_agents = 20
            keys_to_remove = []
            for agentID, agent_info in agent_dict.items():
                if agent_info["type"] == "Fundamentalist" and max_fund_agents > 0:
                    keys_to_remove.append(agentID)
                    max_fund_agents -= 1
            for agentID in keys_to_remove:
                agent_dict.pop(agentID)
                                
        for agentID, agent_info in agent_dict.items():
            if agentID == 0:
                continue #Skip AgentID 0 (Moderator)

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
                agent = agent_info["agent_object"]
                order = agent.trade(LOB.get_trend(), market_price, time)
                if(type(order) == dict):
                    LOB.processOrder(order, False, False)
                x.append(order_num)
                order_num += 1
                y_market_price.append(market_price)
                y_trend.append(LOB.get_trend())

                speculator_proportion = round((num_one_type_init_agent + k * 50) / (num_one_type_init_agent*2 + k * 50),4) * 100
                agent_type = agent_info['type']
                y_agent_type.append([agent_type, str(speculator_proportion) + "%"])
    
        trades = LOB.get_trades()
        for i in range(len(trades)):
            settle = trades[i]
            price = settle['price']
            shares = settle['qty']

            if(settle['party1'][1] == 'bid'):
                party1_agentID = settle['party1'][0]
                party2_agentID = settle['party2'][0]
            
                bidding_agent = agent_dict.get(party1_agentID, {}).get("agent_object")
                asking_agent = agent_dict.get(party2_agentID, {}).get("agent_object")

                bidding_agent.settle_trade(price, shares)
                '''
                If the asking agent that was removed submitted the bid change to moderator
                '''
                if(asking_agent == None):
                    asking_agent = moderator
                asking_agent.settle_trade(price, -shares)

            elif(settle['party1'][1] == 'ask'):
                party1_agentID = settle['party1'][0]
                party2_agentID = settle['party2'][0]

                asking_agent = agent_dict.get(party1_agentID, {}).get("agent_object")
                bidding_agent = agent_dict.get(party2_agentID, {}).get("agent_object")

                asking_agent.settle_trade(price, -shares)
                '''
                If the asking agent that was removed submitted the bid change to moderator
                '''
                if(bidding_agent == None):
                    bidding_agent = moderator
                bidding_agent.settle_trade(price, shares)
            else:
                pass
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=('Market Price', 'Trend'))
    fig.add_trace(pltly.Scatter(x=x, y=y_market_price, mode='lines', name='Market Price', line=dict(color='blue'), hovertext=y_agent_type), row=1, col=1)
    fig.add_trace(pltly.Scatter(x=x, y=y_trend, mode='lines', name='Trend', line=dict(color='red'), hovertext=y_agent_type), row=2, col=1)
    fig.update_layout(height=600, width=800, title_text="Market Price and Trend vs. Time", showlegend=False)
    fig.update_xaxes(title_text='Time', row=2, col=1) 
    # fig.show()

if __name__ == '__main__':
    test_book()