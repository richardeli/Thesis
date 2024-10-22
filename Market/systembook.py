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
import numpy as np
import math

class SystemBook():
    def __init__(self, num_init_fundamentalists=25, num_init_speculators=25, init_upward_market_dir=True, 
                 num_trade_cycles=45, chg_num_agent_pcycle=1, cycle_cool_off_per_dilution=1,
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
        self.cusp_market_price = 0.0
        self.cusp_price_index = 0

        '''TEMP'''
        self.testing_prices = []
        self.testing_volatility = []
        self.volatility_per_cycle = []

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
    
    def start_market(self):
        price = self.LOB.get_market_price()
        for i in range(6):
            if(i % 2 == 0):
                order = {'type': 'limit',
                        'side': 'bid',
                        'qty': 1,
                        'price': price,
                        'agentID': 0,
                        'tid': 0}
                self.LOB.processOrder(order,False,False)
            else:
                order = {'type': 'limit',
                    'side': 'ask',
                    'qty': 1,
                    'price': price*0.95,
                    'agentID': 0,
                    'tid': 0}
                self.LOB.processOrder(order,False,False)
                self.moderator.add_share(order['qty'])

        price = self.LOB.get_market_price()
        for i in range(6):
            order = {'type': 'limit',
                        'side': 'bid',
                        'qty': 1,
                        'price': price,
                        'agentID': 0,
                        'tid': 0}
            self.LOB.processOrder(order,False,False)
            print(self.LOB.get_trend())

    def trade_cycle(self):
        dilution_reversal = False

        #Temp
        temp_ave_prices_p_cycle = []

        for k in range(0, self.num_trade_cycles):
            print("Trade Cycle: {}".format(k))
            if k == self.change_dilution_dir_cycle_num: 
                dilution_reversal = True
            if ((k >= 1) and (k % self.cycle_cool_off_per_dilution) == 0): 
                self.fund_agent_dilution(dilution_reversal)

            ### TEMP
            temp_this_cycle_market_prices = []

            for agentID, agent_info in self.agent_dict.items():
                if agentID == 0:
                    continue 
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

                    ## TEMP
                    temp_this_cycle_market_prices.append(market_price)

            ## TEMP
            average_price = sum(temp_this_cycle_market_prices) / len(temp_this_cycle_market_prices)
            temp_ave_prices_p_cycle.append(average_price)

            self.store_market_price_per_cycle(market_price, k, speculator_proportion)
            self.store_spec_content_vs_ex_demand_per_cycle(speculator_proportion, excess_demand, market_price_change, k)
            self.settle_system_trades()

        #TEMP
        print(temp_ave_prices_p_cycle)
        temp_series = pd.Series(temp_ave_prices_p_cycle)
        temp_return = temp_series.pct_change().dropna()
        this_cycle_volatility = temp_return.std()
        self.volatility_per_cycle.append(this_cycle_volatility)

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
                if(i in range(121,200)):
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
                if(i in range(1,99)):
                    order = {'type': 'limit',
                            'side': 'bid',
                            'qty': 1,
                            'price': i,
                            'agentID': 0,
                            'tid': 0}
                    self.LOB.processOrder(order,False,False)

                if(i in range(101,200)):
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
        window_size = 17500
        min_distance = 200 #250
        
        # Detect peaks in the data set
        peaks, _ = find_peaks(data_series, distance=min_distance)
        peaks = peaks[::-1]  # Reverse the order of peaks

        # Iterate through peaks to find the highest one before a drop
        highest_price = None
        highest_price_index = None
        previous_range = 0

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
                    if(window_condition and (current_range <= previous_range)):
                        highest_price = data_series[window_peak_index]
                        highest_price_index = window_peak_index
                        break
                    previous_range = current_range

        if highest_price is None and highest_price_index is None:
            return 0.0, 0
        else:
            print(highest_price_index)
            return highest_price, highest_price_index

    def compute_cusp_kurtosis(self, mp_data, ed_data, sp_data, start_index, end_index):
        if end_index == 0:
            return None, None, None

        market_price_kurt_data = pd.Series(mp_data[start_index:end_index])
        excess_demand_kurt_data = pd.Series(ed_data[start_index:end_index])
        spec_prop_kurt_data = pd.Series(sp_data[start_index:end_index])

        market_price_kurtosis = round(market_price_kurt_data.kurtosis(), 5)
        excess_demand_kurtosis = round(excess_demand_kurt_data.kurtosis(), 5)
        spec_prop_kurtosis = round(spec_prop_kurt_data.kurtosis(),5)

        return market_price_kurtosis, excess_demand_kurtosis, spec_prop_kurtosis

    def compute_cusp_volatility(self, mp_data, index):
        if index == 0:
            return None, None

        previous_100_prices = mp_data[index-100:index]
        previous_10_prices = mp_data[index-10:index]
    
        previous_100_series = pd.Series(previous_100_prices)
        previous_10_series = pd.Series(previous_10_prices)

        returns_100 = previous_100_series.pct_change().dropna()
        returns_10 = previous_10_series.pct_change().dropna()

        returns_100.replace([np.inf, -np.inf], 0, inplace=True)
        returns_10.replace([np.inf, -np.inf], 0, inplace=True)

        volatility_100 = round(returns_100.std(), 3)
        volatility_10 = round(returns_10.std(), 3)

        return volatility_100, volatility_10

    def compute_overall_volatility_pre_cusp(self, mp_data, start_ind, end_ind):
        if end_ind == 0:
            return None

        mp_data_series = pd.Series(mp_data[start_ind:end_ind])

        returns = mp_data_series.pct_change().dropna()
        returns.replace([np.inf, -np.inf], 0, inplace=True)

        volatility_ovr = round(returns.std(), 3)
        return volatility_ovr

    def compute_cusp_price_difference(self, mp_data, start_ind, end_ind):
        if end_ind == 0:
            return None, None

        previous_100_prices = mp_data[end_ind-100:end_ind]
        all_previous_prices = mp_data[start_ind:end_ind]
        all_previous_series = pd.Series(all_previous_prices)
        previous_100_series = pd.Series(previous_100_prices)

        # print("LEN: {} | st_ind: {} | end_ind: {} | ".format(len(mp_data[end_ind-100:end_ind]), start_ind, end_ind))

        range_all = (all_previous_series.max() - all_previous_series.min()).round(3)
        range_100 = (previous_100_series.max() - previous_100_series.min()).round(3)

        return range_all, range_100

    def save_to_excel(self, num_sims, num_runs):
        self.save_per_simulation_excel(num_sims, num_runs)
        self.save_per_window_excel(num_sims, num_runs)

    def save_per_simulation_excel(self, num_sims, num_runs):
        file_name = "Simulation {}".format(num_sims)
        directory = r'C:\Users\Ricky\Documents\GitHub\Thesis\Data Generated\Simulation\{}'.format(file_name + ".csv")
        # directory = '/Users/richardeli/Downloads/USYD/Thesis/Data Generated/Simulation/{}'.format(file_name + ".csv")
        mp_data = self.y_market_price_per_trade
        ed_data = self.excess_demand_per_trade
        sp_data = self.speculator_proportion_per_trade
        mp_c_data = self.market_price_change_per_trade

        start_index = 0
        cusp_index = self.cusp_price_index
        cusp_found = False
        if cusp_index > 0:
            cusp_found = True

        kurt_mp, kurt_ed, kurt_sp = self.compute_cusp_kurtosis(mp_data, ed_data, sp_data, start_index, cusp_index)
        cusp_vol_100, cusp_vol_10 = self.compute_cusp_volatility(mp_c_data, cusp_index)
        ovr_vol = self.compute_overall_volatility_pre_cusp(mp_c_data, start_index, cusp_index)
        ovr_price_diff, prev_100_price_diff = self.compute_cusp_price_difference(mp_data, start_index, cusp_index)

        if not os.path.exists(directory):
            with open(directory, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Run Number', 'Catastrophe Point Found?', 'Fundamentalists Initialised', 'Speculators Initialised', 'Speculators Added/Removed Per Cycle', 
                                 'Num Cycle', 'Cool off Per Cycle', 'Speculator Proportion at CUSP', 'Market Price at CUSP', 'Excess Demand',
                                 'Kurtosis MP', 'Kurtosis ED', 'Kurtosis SP', 'MP Volatility Last 100 Trades','MP Volatility Last 10 Trades',
                                  'Overall Sim Volatility',  'Pre-CUSP Market Price Difference', 'Last 100 Pre-CUSP Market Prices Difference', 'Total Trades', 'Catastrophe Point Index'])

        new_data_row_to_insert = [
                    num_runs, cusp_found, self.num_init_fundamentalists, self.num_init_speculators, self.chg_num_agent_pcycle,
                    self.num_trade_cycles, self.cycle_cool_off_per_dilution, 
                    self.trade_hovertext[self.cusp_price_index][0] , self.cusp_market_price, self.excess_demand_per_trade[self.cusp_price_index],
                    kurt_mp, kurt_ed, kurt_sp, cusp_vol_100, cusp_vol_10, 
                    ovr_vol, ovr_price_diff, prev_100_price_diff, len(mp_data), cusp_index
        ]

        with open(directory, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(new_data_row_to_insert)
        return
    
    def save_per_window_excel(self, num_sims, num_runs):
        folder_name = "Simulation {}".format(num_sims)
        folder_directory = r'C:\Users\Ricky\Documents\GitHub\Thesis\Data Generated\Window\{}'.format(folder_name)
        # folder_directory = '/Users/richardeli/Downloads/USYD/Thesis/Data Generated/Window/{}'.format(folder_name)

        file_name = "Run {}".format(num_runs)
        file_directory = r'C:\Users\Ricky\Documents\GitHub\Thesis\Data Generated\Window\{}\{}'.format(folder_name, file_name + ".csv")
        # file_directory = '/Users/richardeli/Downloads/USYD/Thesis/Data Generated/Window/{}/{}'.format(folder_name, file_name + ".csv")

        mp_data = self.y_market_price_per_trade
        ed_data = self.excess_demand_per_trade
        sp_data = self.speculator_proportion_per_trade
        mp_c_data = self.market_price_change_per_trade

        cusp_index = self.cusp_price_index
        data_length = len(mp_data)
        start_index = 0
        window_num = 0
        window_size = int(math.ceil(len(mp_data[:cusp_index]) / 100))
        cusp_found = False
        if cusp_index > 0:
            cusp_found = True

        if not os.path.exists(folder_directory):
            os.makedirs(folder_directory)

        if not os.path.exists(file_directory):
            with open(file_directory, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Window Num', 'Num Data Points in Row', 'Speculator Proportion', 'Market Price', 'Excess Demand',
                                 'Kurtosis MP', 'Kurtosis ED', 'Kurtosis SP', 'MP Volatility Last 100 Trades','MP Volatility Last 10 Trades',
                                  'Overall Sim Volatility',  'Pre-CUSP Market Price Difference', 'Last 100 Pre-CUSP Market Prices Difference'])
        
        if cusp_found == True:
            while start_index + window_size <= data_length:
                end_index = start_index + window_size
                kurt_mp, kurt_ed, kurt_sp = self.compute_cusp_kurtosis(mp_data, ed_data, sp_data, start_index, end_index)
                cusp_vol_100, cusp_vol_10 = self.compute_cusp_volatility(mp_c_data, end_index)
                ovr_vol = self.compute_overall_volatility_pre_cusp(mp_c_data, start_index, end_index)
                ovr_price_diff, prev_100_price_diff = self.compute_cusp_price_difference(mp_data, start_index, end_index)
                num_data_points = len(mp_c_data[start_index:end_index])
                window_middle_index = start_index + (end_index - start_index) // 2
                window_avg_market_price = round((sum(mp_data[start_index:end_index]) / len(mp_data[start_index:end_index])), 2)
                                
                new_data_row_to_insert = [
                            window_num, num_data_points, self.trade_hovertext[window_middle_index][0], window_avg_market_price, 
                            self.excess_demand_per_trade[window_middle_index], kurt_mp, kurt_ed, kurt_sp, cusp_vol_100, cusp_vol_10, 
                            ovr_vol, ovr_price_diff, prev_100_price_diff
                ]

                with open(file_directory, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(new_data_row_to_insert)
                
                start_index += window_size
                window_num += 1
                if start_index > cusp_index:
                    return
            
    def save_last_1000_trades_excel(self, num_sims, num_runs):
        folder_name = "Simulation {}".format(num_sims)
        folder_directory = r'C:\Users\Ricky\Documents\GitHub\Thesis\Data Generated\Window\{}'.format(folder_name)
        # folder_directory = '/Users/richardeli/Downloads/USYD/Thesis/Data Generated/Window/{}'.format(folder_name)

        file_name = "Run {}".format(num_runs)
        file_directory = r'C:\Users\Ricky\Documents\GitHub\Thesis\Data Generated\Window\{}\{}'.format(folder_name, file_name + ".csv")
        # file_directory = '/Users/richardeli/Downloads/USYD/Thesis/Data Generated/Window/{}/{}'.format(folder_name, file_name + ".csv")

        mp_data = self.y_market_price_per_trade
        ed_data = self.excess_demand_per_trade
        sp_data = self.speculator_proportion_per_trade
        mp_c_data = self.market_price_change_per_trade

        cusp_index = self.cusp_price_index
        start_index = max(0, cusp_index - 1000)  
        end_index = cusp_index

        cusp_found = False
        if cusp_index > 0:
            cusp_found = True

        if not os.path.exists(folder_directory):
            os.makedirs(folder_directory)

        if not os.path.exists(file_directory):
            with open(file_directory, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Window Num', 'Num Data Points in Row', 'Speculator Proportion', 'Market Price', 'Excess Demand',
                                 'Kurtosis MP', 'Kurtosis ED', 'Kurtosis SP', 'MP Volatility Last 100 Trades','MP Volatility Last 10 Trades',
                                  'Overall Sim Volatility',  'Pre-CUSP Market Price Difference', 'Last 100 Pre-CUSP Market Prices Difference'])
        
        if cusp_found == True:
            for i in range(start_index, end_index):
                kurt_mp, kurt_ed, kurt_sp = self.compute_cusp_kurtosis(mp_data, ed_data, sp_data, i, i + 1)
                cusp_vol_100, cusp_vol_10 = self.compute_cusp_volatility(mp_c_data, i + 1)
                ovr_price_diff, _ = self.compute_cusp_price_difference(mp_data, start_index, i + 1)

                new_data_row_to_insert = [
                    i, mp_data[i], ed_data[i], sp_data[i], kurt_mp, kurt_ed, kurt_sp, 
                    cusp_vol_100, cusp_vol_10, ovr_price_diff
                ]

                with open(file_directory, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(new_data_row_to_insert)

    def save_per_simulation_excel(self, num_sims, num_runs, file_name):
        # directory = r'C:\Users\Ricky\Documents\GitHub\Thesis\Data Generated\{}'.format(file_name + ".csv")
        directory = '/Users/richardeli/Downloads/USYD/Thesis/Data Generated/{}'.format(file_name + ".csv")
        mp_data = self.y_market_price_per_trade
        ed_data = self.excess_demand_per_trade
        sp_data = self.speculator_proportion_per_trade

        if not os.path.exists(directory):
            with open(directory, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Run Number', 'Fundamentalists Initialised', 'Speculators Initialised', 'Speculators Added/Removed Per Cycle', 
                                 'Num Cycle', 'Cool off Per Cycle', 'Speculator Proportion at CUSP', 'Market Price', 'Excess Demand',]
                                )

        new_data_row_to_insert = [
                    num_runs, self.num_init_fundamentalists, self.num_init_speculators, self.chg_num_agent_pcycle,
                    self.num_trade_cycles, self.cycle_cool_off_per_dilution, 
                    self.trade_hovertext[self.cusp_price_index][0] , mp_data[-1], self.excess_demand_per_trade[self.cusp_price_index],
        ]

        with open(directory, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(new_data_row_to_insert)
        return

    def testing_save_vol_excel(self, num_sims, num_runs, file_name):
        # directory = r'C:\Users\Ricky\Documents\GitHub\Thesis\Data Generated\{}'.format(file_name + ".csv")
        directory = '/Users/richardeli/Downloads/USYD/Thesis/Data Generated/{}'.format(file_name + ".csv")
        data = self.volatility_per_cycle

        if not os.path.exists(directory):
            with open(directory, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                'Cycle 1 Volatility', 'Cycle 2 Volatility', 'Cycle 3 Volatility',
                'Cycle 4 Volatility', 'Cycle 5 Volatility', 'Cycle 6 Volatility',
                'Cycle 7 Volatility', 'Cycle 8 Volatility', 'Cycle 9 Volatility',
                'Cycle 10 Volatility',
                'Cycle 1 Average Price', 'Cycle 2 Average Price', 'Cycle 3 Average Price',
                'Cycle 4 Average Price', 'Cycle 5 Average Price', 'Cycle 6 Average Price',
                'Cycle 7 Average Price', 'Cycle 8 Average Price', 'Cycle 9 Average Price',
                'Cycle 10 Average Price',
                'Cycle 1 Speculator Proportion', 'Cycle 2 Speculator Proportion',
                'Cycle 3 Speculator Proportion', 'Cycle 4 Speculator Proportion',
                'Cycle 5 Speculator Proportion', 'Cycle 6 Speculator Proportion',
                'Cycle 7 Speculator Proportion', 'Cycle 8 Speculator Proportion',
                'Cycle 9 Speculator Proportion', 'Cycle 10 Speculator Proportion'
            ])

        new_data_row_to_insert = [
        *self.testing_volatility[:10],  # Volatility values for 10 cycles
        *self.testing_prices[:10],      # Average prices for 10 cycles
        *self.speculator_proportion_per_cycle[:10]  # Speculator proportion for 10 cycles
        ]
        with open(directory, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(new_data_row_to_insert)
        return
    
    def testing_trade_cycle(self):
        dilution_reversal = False

        # TEMP: Store average and intra-cycle prices
        temp_ave_prices_p_cycle = []
        intra_cycle_volatility = []  # Store volatility for each cycle

        for k in range(self.num_trade_cycles):
            print(f"Trade Cycle: {k}")

            # Check for dilution reversal or cool-off events
            if k == self.change_dilution_dir_cycle_num:
                dilution_reversal = True
            if k >= 1 and k % self.cycle_cool_off_per_dilution == 0:
                self.fund_agent_dilution(dilution_reversal)

            # TEMP: Store all market prices within this cycle
            temp_this_cycle_market_prices = []

            # Iterate over agents and execute trades
            for agentID, agent_info in self.agent_dict.items():
                if agentID == 0:  # Skip market maker
                    continue

                time = self.LOB.get_time()
                if self.LOB.get_market_price() is not None:
                    market_price = self.LOB.get_market_price() / 1000
                    agent = agent_info["agent_object"]
                    order = agent.trade(self.LOB.get_trend(), market_price, time)

                    if isinstance(order, dict):
                        self.LOB.processOrder(order, False, False)

                    # Track speculator proportion, demand, and market price change
                    speculator_proportion = self.get_speculator_proportion()
                    excess_demand = self.get_excess_demand()
                    market_price_change = self.calculate_market_price_post_trade(
                        market_price, self.LOB.get_market_price() / 1000
                    )

                    # Store price data for analysis
                    self.store_market_price_per_trade(self.order_num, market_price, speculator_proportion, k)
                    self.store_spec_content_vs_ex_demand_per_trade(speculator_proportion, excess_demand, market_price_change)
                    self.order_num += 1

                    # TEMP: Collect prices within this cycle
                    temp_this_cycle_market_prices.append(market_price)

            # TEMP: Calculate and store average price for this cycle
            # self.speculator_proportion_per_cycle.append(self.get_speculator_proportion())
            average_price = sum(temp_this_cycle_market_prices) / len(temp_this_cycle_market_prices)
            temp_ave_prices_p_cycle.append(average_price)

            # TEMP: Calculate intra-cycle volatility (standard deviation of prices)
            cycle_volatility = pd.Series(temp_this_cycle_market_prices).std()
            intra_cycle_volatility.append(cycle_volatility)

            # Store other cycle data
            self.store_market_price_per_cycle(market_price, k, speculator_proportion)
            self.store_spec_content_vs_ex_demand_per_cycle(speculator_proportion, excess_demand, market_price_change, k)
            self.settle_system_trades()

        # TEMP: Calculate overall volatility based on average prices per cycle
        # print("Average Prices Per Cycle:", temp_ave_prices_p_cycle)
        temp_series = pd.Series(temp_ave_prices_p_cycle)
        temp_return = temp_series.pct_change().dropna()
        overall_volatility = temp_return.std()
        self.volatility_per_cycle.append(overall_volatility)

        # print("Intra-Cycle Volatility:", intra_cycle_volatility)
        # print("Overall Volatility (Avg Prices):", overall_volatility)
        self.testing_prices = temp_ave_prices_p_cycle
        self.testing_volatility = intra_cycle_volatility

        self.cusp_market_price, self.cusp_price_index = self.bifurcation_point_finder()
        return

    def get_vol(self):
        return self.testing_prices, self.testing_volatility