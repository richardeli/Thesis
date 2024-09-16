from Agents.fundamentalist import Fundamentalist
from Agents.speculator import Speculator
from Agents.moderator import Moderator
from Book.orderBook import OrderBook
from Book.orderBook import OrderTree
import random
import pandas as pd
import os 
import csv
import plotly.graph_objects as pltly
from plotly.subplots import make_subplots
from scipy.signal import find_peaks

class SystemBook():
    def __init__(self, save_file_name, num_init_fundamentalists=25, num_init_speculators=25, init_upward_market_dir=True, 
                 num_trade_cycles=75, chg_num_agent_pcycle=20, cycle_cool_off_per_dilution=5,
                 fund_dilute_rm=True, change_dilution_dir_cycle_num=None):
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
        self.save_file_name = save_file_name + ".csv"
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
        self.spec_ex_demand_hovertext_trade = []
        self.market_price_change_per_trade = []

        #Speculative Content vs Excess Demand Per Cycle
        self.speculator_proportion_per_cycle = []
        self.excess_demand_per_cycle = []
        self.spec_ex_demand_hovertext_cycle = []
        self.market_price_change_per_cycle = []

        #CUSP Information
        self.cusp_market_price = 0
        self.cusp_price_index = 0

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
            print("Trade Cycle: {}".format(k))
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
            self.store_market_price_per_cycle(market_price, k, speculator_proportion)
            self.store_spec_content_vs_ex_demand_per_cycle(speculator_proportion, excess_demand, market_price_change, k)
            self.settle_system_trades()
        self.output_graph()
        self.cusp_market_price, self.cusp_price_index = self.bifurcation_point_finder()
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
            self.add_speculators()
        #Add Fundamentalist Agents
        if self.fund_dilute_rm == True and dilution_reversal == True:
            self.add_fundamentalists()
            self.remove_speculators()
        
        #Add Speculator Agents
        if self.fund_dilute_rm == False and dilution_reversal == False:
            self.add_speculators()
            self.remove_fundamentalists()
        
        #Remove Speculator Agents
        if self.fund_dilute_rm == False and dilution_reversal == True:
            self.remove_speculators()
            self.add_fundamentalists()
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
        calc = pre_trade_price - post_trade_price
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
        self.spec_ex_demand_hovertext_trade.append([str(speculator_proportion) + "%", "Excess Demand: " + str(excess_demand)])
        self.market_price_change_per_trade.append(price_change)
        return

    def store_spec_content_vs_ex_demand_per_cycle(self, speculator_proportion, excess_demand, price_change, cycle):
        self.speculator_proportion_per_cycle.append(speculator_proportion)
        self.excess_demand_per_cycle.append(excess_demand)
        self.spec_ex_demand_hovertext_cycle.append([str(speculator_proportion) + "%", "Excess Demand: " + str(excess_demand), "Cycle: " + str(cycle)])
        self.market_price_change_per_cycle.append(price_change)
        return
    
    def output_graph(self):
        fig = make_subplots(rows=2, cols=2, subplot_titles=('Market Price Per Trade', 'Market Price Per Cycle', 'Excess Demand vs Speculative Content Per Trade', 'Excess Demand vs Speculative Content Per Cycle'), vertical_spacing=0.05, row_heights=[0.45, 0.55])
        fig.add_trace(pltly.Scatter(x=self.x_order_num, y=self.y_market_price_per_trade, mode='lines', name='Market Price', line=dict(color='blue'), hovertext=self.trade_hovertext), row=1, col=1)
        fig.add_trace(pltly.Scatter(x=self.x_cycle, y=self.y_market_price_per_cycle, mode='lines', name='Market Price', line=dict(color='red'), hovertext=self.cycle_hovertext), row=1, col=2)
        fig.add_trace(pltly.Scatter(x=self.speculator_proportion_per_trade, y=self.excess_demand_per_trade, mode='lines', name='Excess Demand', line=dict(color='green'), hovertext=self.spec_ex_demand_hovertext_trade), row=2, col=1)
        fig.add_trace(pltly.Scatter(x=self.speculator_proportion_per_cycle, y=self.excess_demand_per_cycle, mode='lines', name='Excess Demand', line=dict(color='purple'), hovertext=self.spec_ex_demand_hovertext_cycle), row=2, col=2)

        fig.update_layout(
            height=1000,
            width=1200,
            title_text="Market Price Over Time",
            showlegend=True,
            xaxis2=dict(tickangle=0)
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

    def bifurcation_point_finder(self):
        data = self.y_market_price_per_trade
        data_series = pd.Series(data)
        
        # Parameters for smoothing
        window_size = 10000
        min_distance = 200 #250
        
        # Detect peaks in the data set
        peaks, _ = find_peaks(data_series, distance=min_distance)
        peaks = peaks[::-1]  # Reverse the order of peaks

        # Iterate through peaks to find the highest one before a drop
        highest_price = None
        highest_price_index = None
        previous_range = None

        for peak in peaks: #Peak list iteration
            if peak > 0:
                if peak + window_size < len(data_series):
                    start_index = peak
                    end_index = peak + window_size
                    window = data_series[start_index:end_index + 1]

                    window_max = window.max()
                    window_min = window.min()
                    current_range = window_max - window_min

                    window_peak_index = window.idxmax()
                    window_condition = window_max > window_min * 50
                    print("Max: {} ||| Ind: {} ||| Min: {} ||| Ind: {} ||| Condition: {}".format(window_max, window_peak_index, window_min, end_index, window_condition))
                    if(window_condition and (current_range <= previous_range)):
                        highest_price = data_series[window_peak_index]
                        highest_price_index = window_peak_index
                        break
                    previous_range = current_range

        if highest_price is not None and highest_price_index is not None:
            print(f"Highest market price before significant drop: {highest_price}")
            print(f"Index of the highest market price: {highest_price_index}")
        else:
            print("No significant drop detected.")
            return 0, 0
        
        return highest_price, highest_price_index

    def save_to_excel(self, filename):
        directory = r'C:\Users\Ricky\Documents\GitHub\Thesis\Data Generated\{}'.format(filename + ".csv")

        if not os.path.exists(directory):
            with open(directory, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Fundamentalists Initialised', 'Speculators Initialised', 'Speculators Added/Removed Per Cycle', 
                                 'Num Cycle', 'Cool off Per Cycle', 'Speculator Proportion at CUSP', 'Market Price at CUSP'])
                        
        new_data_row_to_insert = [
            self.num_init_fundamentalists, self.num_init_speculators, self.chg_num_agent_pcycle,
                    self.num_trade_cycles, self.cycle_cool_off_per_dilution, 
                    self.trade_hovertext[self.cusp_price_index][0] , self.cusp_market_price
        ]

        with open(directory, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(new_data_row_to_insert)

