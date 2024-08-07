from Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Agents.moderator import Moderator
from Book.orderBook import OrderBook
from Book.orderBook import OrderTree
import plotly.graph_objects as pltly
from plotly.subplots import make_subplots

class SystemBook():
    def __init__(self, num_init_agents=25, initial_market_correction_dir=1, num_trade_cycles=50, chg_num_agent_pcycle=20, fundamentalist_dilution=1):
        self.agent_dict = {}
        self.moderator = Moderator()
        self.LOB = OrderBook()
        self.num_one_type_init_agent = num_init_agents 
        self.num_trade_cycles = num_trade_cycles
        self.chg_num_agent_pcycle = chg_num_agent_pcycle
        self.initial_market_correction_dir = initial_market_correction_dir
        self.fundamentalist_dilution = fundamentalist_dilution
        self.ids = 1
        self.init_agent_LOB_environment()
        self.init_market_direction()

        #Graphing Stuff
        self.order_num = 0
        self.x = []
        self.y_market_price = []
        self.y_trend = []
        self.y_agent_type = []


    def init_agent_LOB_environment(self):
        self.agent_dict[self.moderator.get_agentID()] = {
                "agent_object": self.moderator,
                "type": "Moderator"
        }

        for i in range(self.num_one_type_init_agent):
            fund_agent = Fundamentalist(self.ids, 100000)
            spec_agent = Speculator(self.ids + 1, 100000)
            self.ids += 2
            fund_agent.set_shares(1)
            spec_agent.set_shares(1)
            self.agent_dict[fund_agent.get_agentID()] = {
                "agent_object": fund_agent,
                "type": "Fundamentalist"
            }

            # Add Speculator agent to the dictionary
            self.agent_dict[spec_agent.get_agentID()] = {
                "agent_object": spec_agent,
                "type": "Speculator"
            }
        return

    def trade_cycle(self):
        for k in range(0, self.num_trade_cycles):
            if k >= 1:
                self.fund_agent_dilution()
            print(f"Cycle {k}: {len(self.agent_dict)} agents")
                         
            for agentID, agent_info in self.agent_dict.items():
                if agentID == 0:
                    continue #Skip AgentID 0 (Moderator)

                time = self.LOB.get_time()
                if(self.LOB.get_market_price() != None):

                    '''Decide how to determine market price
                    by using the bestAsk/bestBid() as market price the result is more in-line with expectation
                    when market price is the midpoint it stacking occurs between the agents so the price never moves
                    and market price goes stagnant'''

                    '''To assure market liquidity we will be simulating the market price not as them paying the market price itself but paying an additional premium
                    in this case we will enact it as 5% of the market price as additional cost 
                    When bidding this means and increase of 5%'''
                    market_price = self.LOB.get_market_price() / 1000
                    agent = agent_info["agent_object"]
                    order = agent.trade(self.LOB.get_trend(), market_price, time)
                    if(type(order) == dict):
                        self.LOB.processOrder(order, False, False)

                    speculator_proportion = self.get_speculator_proportion()
                    agent_type = agent_info['type']

                    self.store_market_price_information(self.order_num, market_price, self.LOB.get_trend(), speculator_proportion, agent_type)
                    self.order_num += 1 
            self.settle_system_trades()
        self.output_market_price_graph()
        # print(len(self.agent_dict))
        return

    def init_market_direction(self):
        '''DOWNWARDS PRESSURE'''
        if(self.initial_market_correction_dir == 0):
            for i in range(1,200):
                if(i in range(1,120)):
                    order = {'type': 'limit',
                            'side': 'bid',
                            'qty': 1,
                            'price': i,
                            'agentID': 0,
                            'tid': 0}
                    self.LOB.processOrder(order,False,False)
                if(i in range(130,200)):
                    order = {'type': 'limit',
                        'side': 'ask',
                        'qty': 1,
                        'price': i,
                        'agentID': 0,
                        'tid': 0}
                    self.LOB.processOrder(order,False,False)
                    self.moderator.add_share(order['qty'])
                else:
                    pass

        '''UPWARDS PRESSURE'''
        if(self.initial_market_correction_dir == 1):
            for i in range(1,200):
                if(i in range(1,80)):
                    order = {'type': 'limit',
                            'side': 'bid',
                            'qty': 1,
                            'price': i,
                            'agentID': 0,
                            'tid': 0}
                    self.LOB.processOrder(order,False,False)

                if(i in range(90,200)):
                    order = {'type': 'limit',
                        'side': 'ask',
                        'qty': 1,
                        'price': i,
                        'agentID': 0,
                        'tid': 0}
                    self.LOB.processOrder(order,False,False)
                    self.moderator.add_share(order['qty'])
                else:
                    pass
        else:
            print("No valid direction given")
        return
    
    def get_speculator_proportion(self):
        #Fundamentalists being removed
        if self.fundamentalist_dilution == 0:
            speculator_proportion = round((self.num_one_type_init_agent / (len(self.agent_dict)-1)),4) * 100

        #Speculators being added
        if self.fundamentalist_dilution == 1:
            speculator_proportion = round(1-(self.num_one_type_init_agent / (len(self.agent_dict)-1)),4) * 100
            # print('WWWW')
            # print(str(self.num_one_type_init_agent) + "|" + str(len(self.agent_dict)-1))
            # print('WWWW')

        else:
            return
        return speculator_proportion

    def fund_agent_dilution(self):
        #Remove Fundamentalist Agents
        if self.fundamentalist_dilution == 0:
            self.remove_fundamentalists()
        
        #Add Speculator Agents
        if self.fundamentalist_dilution == 1:
            self.add_speculators()
        else:
            pass
        return
    
    def add_speculators(self):
        for i in range(self.chg_num_agent_pcycle):
            spec_agent = Speculator(self.ids, 100000)
            self.ids += 1
            spec_agent.set_shares(1)
            self.agent_dict[spec_agent.get_agentID()] = {
                "agent_object": spec_agent,
                "type": "Speculator"
            }
        return
    
    def remove_fundamentalists(self):
        max_fund_agents = self.chg_num_agent_pcycle
        keys_to_remove = []
        for agentID, agent_info in self.agent_dict.items():
            if agent_info["type"] == "Fundamentalist" and max_fund_agents > 0:
                keys_to_remove.append(agentID)
                max_fund_agents -= 1
        for agentID in keys_to_remove:
            self.agent_dict.pop(agentID)
        return

    def settle_system_trades(self):
        trades = self.LOB.get_trades()
        for i in range(len(trades)):
            settle = trades[i]
            price = settle['price']
            shares = settle['qty']

            if(settle['party1'][1] == 'bid'):
                party1_agentID = settle['party1'][0]
                party2_agentID = settle['party2'][0]
            
                bidding_agent = self.agent_dict.get(party1_agentID, {}).get("agent_object")
                asking_agent = self.agent_dict.get(party2_agentID, {}).get("agent_object")

                if(bidding_agent == None):
                    bidding_agent = self.moderator
                bidding_agent.settle_trade(price, shares)
                '''
                If the asking agent that was removed submitted the bid change to moderator
                '''
                if(asking_agent == None):
                    asking_agent = self.moderator
                asking_agent.settle_trade(price, -shares)

            elif(settle['party1'][1] == 'ask'):
                party1_agentID = settle['party1'][0]
                party2_agentID = settle['party2'][0]

                asking_agent = self.agent_dict.get(party1_agentID, {}).get("agent_object")
                bidding_agent = self.agent_dict.get(party2_agentID, {}).get("agent_object")

                if(asking_agent == None):
                    asking_agent = self.moderator
                asking_agent.settle_trade(price, -shares)
                '''
                If the asking agent that was removed submitted the bid change to moderator
                '''
                if(bidding_agent == None):
                    bidding_agent = self.moderator
                bidding_agent.settle_trade(price, shares)
            else:
                pass

    def store_market_price_information(self, order_num, y_market_price, y_trend, speculator_proportion, y_agent_type):
        self.x.append(order_num)
        self.y_market_price.append(y_market_price)
        self.y_trend.append(y_trend)
        self.y_agent_type.append([y_agent_type, str(speculator_proportion) + "%"])
        return
    
    def output_market_price_graph(self):
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=('Market Price', 'Trend'))
        fig.add_trace(pltly.Scatter(x=self.x, y=self.y_market_price, mode='lines', name='Market Price', line=dict(color='blue'), hovertext=self.y_agent_type), row=1, col=1)
        fig.add_trace(pltly.Scatter(x=self.x, y=self.y_trend, mode='lines', name='Trend', line=dict(color='red'), hovertext=self.y_agent_type), row=2, col=1)
        fig.update_layout(height=600, width=800, title_text="Market Price and Trend vs. Time", showlegend=False)
        fig.update_xaxes(title_text='Time', row=2, col=1) 
        fig.show()
        return