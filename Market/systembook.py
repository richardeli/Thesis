from Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Agents.moderator import Moderator
from Book.orderBook import OrderBook
from Book.orderBook import OrderTree
import plotly.graph_objects as pltly
from plotly.subplots import make_subplots

class SystemBook():
    def __init__(self, num_init_agents=25, init_upward_market_dir=True, num_trade_cycles=75, chg_num_agent_pcycle=20, fund_dilute_rm=True, change_dilution_dir_cycle_num=None):
        self.agent_dict = {}
        self.moderator = Moderator()
        self.LOB = OrderBook()
        self.num_one_type_init_agent = num_init_agents
        self.num_trade_cycles = num_trade_cycles
        self.chg_num_agent_pcycle = chg_num_agent_pcycle
        self.init_upward_market_dir = init_upward_market_dir
        self.fund_dilute_rm = fund_dilute_rm
        self.ids = 1
        self.init_agent_LOB_environment()
        self.init_market_direction()

        self.change_dilution_dir_cycle_num = change_dilution_dir_cycle_num

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
        dilution_reversal = False
        for k in range(0, self.num_trade_cycles):
            if k == self.change_dilution_dir_cycle_num: #Change direction of dilution (reversal) 
                dilution_reversal = True

            if k >= 1: #Let first trade cycle occur with no agent dilution
                self.fund_agent_dilution(dilution_reversal) 
                         
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

                    speculator_proportion = round(self.get_speculator_proportion(),2)
                    agent_type = agent_info['type']

                    self.store_market_price_information(self.order_num, market_price, self.LOB.get_trend(), speculator_proportion, agent_type, k)
                    self.order_num += 1 
            self.settle_system_trades()
        self.output_market_price_graph()
        return

    def init_market_direction(self):
        '''DOWNWARDS PRESSURE'''
        if(self.init_upward_market_dir == False):
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
        if(self.init_upward_market_dir == True):
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
        return
    
    def get_speculator_proportion(self):
        #Fundamentalists being removed
        if self.fund_dilute_rm == True:
            speculator_proportion = (self.num_one_type_init_agent / (len(self.agent_dict)-1)) * 100

        #Speculators being added
        if self.fund_dilute_rm == False:
            speculator_proportion = 1-(self.num_one_type_init_agent / (len(self.agent_dict)-1)) * 100
        return speculator_proportion

    def fund_agent_dilution(self, dilution_reversal):
        #Remove Fundamentalist Agents
        if self.fund_dilute_rm == True and dilution_reversal == False:
            self.remove_fundamentalists()
        #Add Fundamentalist Agents
        if self.fund_dilute_rm == True and dilution_reversal == True:
            self.add_fundamentalists()
        
        #Add Speculator Agents
        if self.fund_dilute_rm == False and dilution_reversal == False:
            self.add_speculators()
        
        #Remove Speculator Agents
        if self.fund_dilute_rm == False and dilution_reversal == True:
            self.remove_speculators()
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
    
    def count_speculators(self):
        count = 0
        for agentID, agent_info in self.agent_dict.items():
            agent_type = agent_info['type']
            if agent_type == "Speculator":
                count += 1
        return count
    
    def add_fundamentalists(self):
        for i in range(self.chg_num_agent_pcycle):
            fund_agent = Fundamentalist(self.ids, 100000)
            self.ids += 1
            fund_agent.set_shares(1)
            self.agent_dict[fund_agent.get_agentID()] = {
                "agent_object": fund_agent,
                "type": "Fundamentalist"
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

    def remove_speculators(self):
        max_spec_agents = self.chg_num_agent_pcycle
        keys_to_remove = []
        for agentID, agent_info in self.agent_dict.items():
            if agent_info["type"] == "Speculator" and max_spec_agents > 0:
                keys_to_remove.append(agentID)
                max_spec_agents -= 1
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

    def store_market_price_information(self, order_num, y_market_price, y_trend, speculator_proportion, y_agent_type, trade_cycle):
        self.x.append(order_num)
        self.y_market_price.append(y_market_price)
        self.y_trend.append(y_trend)
        self.y_agent_type.append([y_agent_type, str(speculator_proportion) + "%", "Cycle: " + str(trade_cycle)])
        return
    
    def output_market_price_graph(self):
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=('Market Price', 'Trend'))
        fig.add_trace(pltly.Scatter(x=self.x, y=self.y_market_price, mode='lines', name='Market Price', line=dict(color='blue'), hovertext=self.y_agent_type), row=1, col=1)
        fig.add_trace(pltly.Scatter(x=self.x, y=self.y_trend, mode='lines', name='Trend', line=dict(color='red'), hovertext=self.y_agent_type), row=2, col=1)
        fig.update_layout(height=600, width=800, title_text="Market Price and Trend vs. Time", showlegend=False)
        fig.update_xaxes(title_text='Time', row=2, col=1) 
        fig.show()
        return