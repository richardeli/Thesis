import numpy as np
import random
import math

class Speculator():
    '''
    WHEN COMPUTING TRADE LOGIC DO PROBABIILITY DISITRUBUTION BASED ON LEVEL OF PRICE MOVEMENT I.E.
    1 UP (20% CHANCE TO TRADE), 2 UP (30% CHANCE TO TRADE), 3 UP (40% CHANCE TO TRADE) ETC. TO MAYBE 5
    1 DOWN (20% CHANCE TO TRADE), 2 DOWN (30% CHANCE TO TRADE), 3 DOWN (40% CHANCE TO TRADE) ETC. TO MAYBE 5
    RANDOMISED THE PROBABILITY OF EACH SPECULATOR'S PROBABILITY FOR TRADE AT EACH LEVEL

    N.B. WILL NEED TO COMPUTE ORDERBOOK PRICE MOVEMENTS LOGIC TO PASS IN A DICT MAYBE OF WHAT EACH PRICE MOVEMENT LEVEL CHANGE IS:
    LAST 5 = 5 UP, LAST 4 = 3 UP 1 DOWN, LAST 3 = 3 UP BUT LET IT MAKE SENSE
    '''
    def __init__(self, agentID, inital_cash, scale=1.0):        
        self.money = inital_cash
        self.agentID = agentID
        self.shares = 0
        self.type = "Speculator"

        #Non-ordered trend probabilities
        # self.probabilities = {i: 1 - np.exp(-random.expovariate(scale)) for i in range(-5, 6) if i != 0}

        #Ordered trend probabilities
        self.probabilities = {}
        # Generate probabilities for negative values (-5 to -1) and sort in descending order
        self.probabilities.update({i: 1 - np.exp(-random.expovariate(scale)) for i in range(-5, 0)})
        self.probabilities.update({i: 1 - np.exp(-random.expovariate(scale)) for i in range(1, 6)})
        # Sort the dictionary by absolute value of keys in descending order
        self.probabilities = dict(sorted(self.probabilities.items(), key=lambda item: item[0] if item[0] < 0 else -item[0]))

    def set_shares(self, new_shares):
        self.shares = new_shares
        return
    def get_shares(self):
        return self.shares
    
    def set_agentId(self, new_agentID):
        self.agentID = new_agentID
        return
    def get_agentID(self):
        return self.agentID
    
    def set_money(self, new_money):
        self.money = new_money
        return
    def get_money(self):
        return self.money
    
    def get_agentType(self):
        return self.type
    
    def trade(self, trend, market_price, time):
        #Randomises whether agent will be buyer or seller for the round
        ## seller (buyer = 0) | buyer (buyer = 1)
        if(trend == 0):
            return
        
        #Get probability somewhere between 0.05 - 150 (exponential probability)
        buy_probability = self.probabilities[trend]
        # buy_probability = self.probabilities[abs(trend) - 1]  

        #if trends is negative then invert buy_probability
        if(trend < 0):
            buy_probability = 1 - buy_probability

        buy = np.random.choice([True, False], p=(buy_probability, 1 - buy_probability))
        num_shares_purchasable = math.floor(self.money / market_price)

        if(buy):
            if(num_shares_purchasable >= 1):
                order = {'type': 'limit',
                        'side': 'bid',
                        'qty': 1,
                        'price': round(market_price*1.05,1),
                        'tid': time,
                        'agentID': self.agentID}
                return order
        else:
            if(self.shares > 0):
                num_shares_to_sell = self.shares
                order = {'type': 'limit',
                        'side': 'ask',
                        'qty': num_shares_to_sell,
                        'price': round(market_price*0.95,1),
                        'tid': time,
                        'agentID': self.agentID}
                return order
        return
    
    def settle_trade(self, price, shares):
        if(shares > 0):  # Buying shares (positive shares)
            self.money -= shares * price
            self.shares += shares
            
        elif(shares < 0):  # Selling shares (negative shares)
            self.money += abs(shares) * price
            self.shares -= abs(shares)