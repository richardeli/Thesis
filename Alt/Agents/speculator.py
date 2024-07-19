import numpy as np
import random
import math

class Speculator():
    def __init__(self, agentID, inital_cash):
        self.volatility_threshold = random.randint(0, 20)
        
        self.money = inital_cash
        self.agentID = agentID
        self.shares = 0

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

    def set_volatility_threshold(self, new_volatility):
        self.volatility_threshold = new_volatility
        return
    def get_volatility_threshold(self):
        return self.volatility_threshold

    

    def trade(self, market_volatility, market_price):
        #Randomises whether agent will be buyer or seller for the round
        ## seller (buyer = 0) | buyer (buyer = 1)
        buyer = np.random.choice([True, False])
        
        #Buyer Logic
        if(market_volatility > self.volatility_threshold):

            num_shares_purchasable = self.money / market_price 
            num_shares_to_purchase = math.floor(num_shares_purchasable)
            order = {'type': 'bid',
                    'qty': num_shares_to_purchase,
                    'price': market_price,
                    'agentID': self.agentID}
            return order
        
        #Seller Logic
        elif(market_volatility < -(self.volatility_threshold) & self.shares > 0):
            num_shares_to_sell = self.shares

            order = {'type': 'ask',
                    'qty': num_shares_to_sell,
                    'price': market_price,
                    'agentID': self.agentID}
            return order
        else:
            return 0
    
    def settle_trade(self, shares, price):
        return