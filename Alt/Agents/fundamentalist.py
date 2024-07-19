import numpy as np
import random
import math

class Fundamentalist():
    def __init__(self, agentID, inital_cash):

        self.estimated_price = random.randint(90, 110)

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

    def set_estimate_price(self, new_estimate):
        self.estimated_price = new_estimate
        return
    def get_estimate_price(self):
        return self.estimated_price

    def trade(self, market_price, time):
        #Randomises whether agent will be buyer or seller for the round
        ## seller (buyer = 0) | buyer (buyer = 1)
        buyer = False
        
        #Determine if buy or sell
        if(market_price == self.estimated_price):
            return 0
        elif(market_price < self.estimated_price):
            buyer = True

        #Buyer Logic
        if(buyer == True):
            num_shares_purchasable = self.money / market_price 
            num_shares_to_purchase = math.floor(num_shares_purchasable)
            order = {'type': 'bid',
                    'qty': num_shares_to_purchase,
                    'price': self.estimated_price,
                    'agentID': self.agentID,
                    'tid' : time}
            return order
        #Seller Logic
        else:
            if(self.shares > 0):
                num_shares_to_sell = self.shares

                order = {'type': 'ask',
                        'qty': num_shares_to_sell,
                        'price': self.estimated_price,
                        'agentID': self.agentID,
                         'tid' : time}
                return order
            return 0
    
    def settle_trade(self, shares, price):
        return