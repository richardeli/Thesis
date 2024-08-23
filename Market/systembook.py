from Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Agents.moderator import Moderator
from Book.orderBook import OrderBook
from Book.orderBook import OrderTree
import plotly.graph_objects as pltly
import random
from plotly.subplots import make_subplots

class SystemBook():
    def __init__(self, num_init_fundamentalists=25, num_init_speculators=25, init_upward_market_dir=True, num_trade_cycles=75, chg_num_agent_pcycle=20, cycle_cool_off_per_dilution=5,fund_dilute_rm=True, change_dilution_dir_cycle_num=None):
        self.agent_dict = {}
        self.moderator = Moderator()
        self.LOB = OrderBook()
        self.num_init_fundamentalists = num_init_fundamentalists
        self.num_init_speculators = num_init_speculators
        self.num_trade_cycles = num_trade_cycles
        self.chg_num_agent_pcycle = chg_num_agent_pcycle
        self.init_upward_market_dir = init_upward_market_dir
        self.fund_dilute_rm = fund_dilute_rm
        self.cycle_cool_off_per_dilution = cycle_cool_off_per_dilution
        self.ids = 1
        self.init_agent_LOB_environment()
        self.init_market_direction()

        self.change_dilution_dir_cycle_num = change_dilution_dir_cycle_num

        #Graphing Stuff
        #Market Price Per Trade
        self.order_num = 0
        self.x_order_num = []
        self.y_market_price_per_trade = []
        self.trade_hovertext = []

        #Market Price Per Cycle
        self.x_cycle = []
        self.y_market_price_per_cycle = []
        self.cycle_hovertext = []

        #Speculative Content vs Excess Demand Per Trade
        self.speculator_proportion_per_trade = []
        self.excess_demand_per_trade = []
        self.spec_ex_demand_hovertext = []
        self.market_price_change_per_trade = []

    def init_agent_LOB_environment(self):
        self.agent_dict[self.moderator.get_agentID()] = {
                "agent_object": self.moderator,
                "type": "Moderator"
        }
        
        #Add all fundamentalists
        for i in range(self.num_init_fundamentalists):
            fund_agent = Fundamentalist(self.ids, 100000)
            self.ids += 1
            fund_agent.set_shares(1)
            self.agent_dict[fund_agent.get_agentID()] = {
                "agent_object": fund_agent,
                "type": "Fundamentalist"
            }

        #Add all speculators 
        for i in range(self.num_init_speculators):
            spec_agent = Speculator(self.ids, 100000)
            self.ids += 1
            spec_agent.set_shares(1)
            self.agent_dict[spec_agent.get_agentID()] = {
                "agent_object": spec_agent,
                "type": "Speculator"
            }
            
        keys = list(self.agent_dict.keys())
        random.shuffle(keys)
        shuffled_agent_dict = {key: self.agent_dict[key] for key in keys}
        self.agent_dict = shuffled_agent_dict


        return

    def trade_cycle(self):
        dilution_reversal = False
        for k in range(0, self.num_trade_cycles):
            if k == self.change_dilution_dir_cycle_num: #Change direction of dilution (reversal)
                dilution_reversal = True

            if ((k >= 1) and (k % self.cycle_cool_off_per_dilution) == 0): #Let first trade cycle occur with no agent dilution
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
                    speculator_proportion = self.get_speculator_proportion()
                    excess_demand = self.get_excess_demand()
                    market_price_change = self.calculate_market_price_post_trade(market_price, self.LOB.get_market_price() / 1000)

                    self.store_market_price_per_trade(self.order_num, market_price, speculator_proportion, k)
                    self.store_spec_content_vs_ex_demand_per_trade(speculator_proportion, excess_demand, market_price_change)
                    self.order_num += 1
            self.store_market_price_per_cycle((self.LOB.get_market_price() / 1000), k, self.get_speculator_proportion())
            self.settle_system_trades()
        # self.output_market_price_graph()
        self.output_spec_content_vs_ex_demand_graph_on_bottom()
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
        for i in range(1,100):
            price_ceiling = {'type': 'limit',
                            'side': 'ask',
                            'qty': 100000,
                            'price': 200,
                            'agentID': 0,
                            'tid': 0}
            price_floor = {'type': 'limit',
                            'side': 'bid',
                            'qty': 100000,
                            'price': 1,
                            'agentID': 0,
                            'tid': 0}
            self.LOB.processOrder(price_ceiling,False,False)
            self.LOB.processOrder(price_floor,False,False)
            self.moderator.add_share(price_ceiling['qty'])
            self.moderator.add_share(price_floor['qty'])
        return
    
    def get_speculator_proportion(self):
        total_agents = len(self.agent_dict) - 1
        if total_agents <= 0:
            return 0 
        num_speculators = self.count_speculators()
        speculator_proportion = (num_speculators / total_agents) * 100
        return round(speculator_proportion,4)

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
    
    def get_excess_demand(self):
        demand = self.LOB.get_num_bids()
        supply = self.LOB.get_num_asks()
        excess_demand = demand - supply
        return excess_demand

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
    
    def calculate_market_price_post_trade(self, pre_trade_price, post_trade_price):
        calc = abs(pre_trade_price - post_trade_price)
        return calc

    def store_market_price_per_trade(self, order_num, y_market_price, speculator_proportion, trade_cycle):
        self.x_order_num.append(order_num)
        self.y_market_price_per_trade.append(y_market_price)
        self.trade_hovertext.append([str(speculator_proportion) + "%", "Cycle: " + str(trade_cycle)])
        return
    
    def store_market_price_per_cycle(self, y_market_price, trade_cycle, speculator_proportion):
        self.y_market_price_per_cycle.append(y_market_price)
        self.x_cycle.append(str(trade_cycle))
        self.cycle_hovertext.append([str(speculator_proportion) + "%", "Cycle: " + str(trade_cycle)])

    def store_spec_content_vs_ex_demand_per_trade(self, speculator_proportion, excess_demand, price_change):
        self.speculator_proportion_per_trade.append(speculator_proportion)
        self.excess_demand_per_trade.append(excess_demand)
        self.spec_ex_demand_hovertext.append([str(speculator_proportion) + "%", "Excess Demand: " + str(excess_demand)])
        self.market_price_change_per_trade.append(price_change)
        return

    def output_market_price_graph(self):
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=('Market Price Per Trade', 'Market Price Per Cycle'), vertical_spacing=0.1)
        fig.add_trace(pltly.Scatter(x=self.x_order_num, y=self.y_market_price_per_trade, mode='lines', name='Trade', line=dict(color='blue'), hovertext=self.trade_hovertext), row=1, col=1)
        fig.add_trace(pltly.Scatter(x=self.x_cycle, y=self.y_market_price_per_cycle, mode='lines', name='Cycle', line=dict(color='red'), hovertext=self.cycle_hovertext), row=2, col=1)
        fig.update_layout(
            height=700,
            width=800,
            title_text="Market Price Over Time",
            showlegend=True,
        )
        fig.add_annotation(
            text="Initialised Fundamentalists: {}<br>Initialised Speculators: {}<br>Number Of Agents Changed Per Cycle: {}<br>Number Of Cycles For Cooling Off Period Between Each Change: {}".format(
                self.num_init_fundamentalists, 
                self.num_init_speculators, 
                self.chg_num_agent_pcycle, 
                self.cycle_cool_off_per_dilution),
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.16,  # Positioning it below the plot
            showarrow=False,
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color="black"
            ),
            align="center",
            bgcolor="white",  # Background color for better readability
            bordercolor="black",
            borderwidth=1
        )
        fig.update_xaxes(title_text='Time', row=2, col=1) 
        fig.show()
        return

    def output_spec_content_vs_ex_demand_graph_on_bottom(self):
        fig = make_subplots(rows=2, cols=2, subplot_titles=('Market Price Per Trade', 'Market Price Per Cycle', 'Speculative Content vs Excess Demand Per Trade'), vertical_spacing=0.05, row_heights=[0.45, 0.55])
        fig.add_trace(pltly.Scatter(x=self.x_order_num, y=self.y_market_price_per_trade, mode='lines', name='Market Price', line=dict(color='blue'), hovertext=self.trade_hovertext), row=1, col=1)
        fig.add_trace(pltly.Scatter(x=self.x_cycle, y=self.y_market_price_per_cycle, mode='lines', name='Market Price', line=dict(color='red'), hovertext=self.cycle_hovertext), row=1, col=2)
        fig.add_trace(pltly.Scatter(x=self.speculator_proportion_per_trade, y=self.excess_demand_per_trade, mode='lines', name='Excess Demand', line=dict(color='green'), hovertext=self.spec_ex_demand_hovertext), row=2, col=1)
        fig.update_layout(
            height=1000,
            width=1200,
            title_text="Market Price Over Time",
            showlegend=True,
        )
        fig.add_annotation(
            text="Initialised Fundamentalists: {}<br>Initialised Speculators: {}<br>Number Of Agents Changed Per Cycle: {}<br>Number Of Cycles For Cooling Off Period Between Each Change: {}".format(
                self.num_init_fundamentalists, 
                self.num_init_speculators, 
                self.chg_num_agent_pcycle, 
                self.cycle_cool_off_per_dilution),
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.1,  
            showarrow=False,
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color="black"
            ),
            align="center",
            bgcolor="white",  
            bordercolor="black",
            borderwidth=1
        )
        fig.show()

    # def output_spec_content_vs_ex_demand_graph_on_bottom(self):
    #     fig = make_subplots(rows=2, cols=1)

    #     # Speculative Content vs Excess Demand Per Trade with colored markers
    #     fig.add_trace(
    #         pltly.Scatter(
    #             x=self.speculator_proportion_per_trade,
    #             y=self.excess_demand_per_trade,
    #             mode='markers',
    #             marker=dict(
    #                 size=10,
    #                 color=self.market_price_change_per_trade,  # Color by market price change
    #                 colorscale='Viridis',  # Choose a colorscale
    #                 colorbar=dict(
    #                     title="Market Price Change"
    #                 ),
    #             ),
    #             text=self.spec_ex_demand_hovertext,
    #             name="Speculative Content vs Excess Demand"
    #         ),
    #         row=1, col=1
    #     )

    #     # Market Price Per Trade without coloring
    #     fig.add_trace(
    #         pltly.Scatter(
    #             x=self.x_order_num,
    #             y=self.y_market_price_per_trade,
    #             mode='lines+markers',
    #             marker=dict(
    #                 size=6,
    #                 color='blue'  # Default color for market price graph
    #             ),
    #             text=self.trade_hovertext,
    #             name="Market Price Per Trade"
    #         ),
    #         row=2, col=1
    #     )

    #     fig.update_layout(
    #         height=800,
    #         title_text="Speculative Content vs Excess Demand Per Trade and Market Price Per Trade"
    #     )

    #     fig.show()

