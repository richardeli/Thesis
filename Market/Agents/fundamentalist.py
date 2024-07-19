import numpy as np
import random
import math

class Fundamentalist():
    def __init__(self, agentID, initial_cash, price_noise_std=5):
        """
        Initializes the Fundamentalist agent.

        Args:
            agentID (int): Unique identifier for the agent.
            initial_cash (float): Initial cash balance of the agent.
            price_noise_std (float, optional): Standard deviation for random noise added to estimated price. Defaults to 5.
            buy_threshold (float, optional): Threshold for buying relative to estimated price (0-1). Defaults to 0.8.
        """

        #self.estimated_price = (random.randint(90, 110) + np.random.normal(scale=price_noise_std))
        self.estimated_price = random.randint(90, 110)
        self.money = initial_cash
        self.agentID = agentID
        self.shares = 0
        self.type = "Fundamentalist"

    """ GETTER AND SETTER METHODS"""
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

    def set_estimate_price(self, new_estimate):
        self.estimated_price = new_estimate
        return

    def get_estimate_price(self):
        return self.estimated_price

    def trade(self, trend, market_price, time):
        """
        Decides whether to place a buy or sell order based on market conditions.

        Args:
            market_price (float): Current market price.
            LOB (OrderBook): Reference to the order book object.
            time (int): Current simulation time.

        Returns:
            dict or None: Order dictionary if placing an order, None otherwise.
        """
        # Randomly choose between buying (True) or selling (False) with a bias
        if(market_price is None):
            return None

        # Don't trade if market price matches estimated price
        if(market_price == self.estimated_price):
            return None

        # Buying Logic
        if(market_price < self.estimated_price):
            # Check if market price is below a threshold of estimated price
                # Check affordability (consider order book pressure)
            max_affordable_shares = math.floor(self.money / market_price)

            if(max_affordable_shares >= 1):
                # Only buy if affordable and ask price isn't too high
                #num_shares_to_purchase = max_affordable_shares
                num_shares_to_purchase = 1
                order = {'type': 'limit',
                            'side': 'bid',
                            'qty': num_shares_to_purchase,
                            'price': round(market_price,1),
                            'tid': time,
                            'agentID': self.agentID}
                return order
                
        # Selling Logic
        else:
            if(self.shares > 0):
                order = {'type': 'limit',
                         'side': 'ask',
                         'qty': self.shares,
                         'price': round(market_price,1),
                         'tid': time,
                         'agentID': self.agentID,}
                return order
        return "3"  # No order to place

    def settle_trade(self, price, shares):
        if shares > 0:  # Bought shares (positive shares)
            self.money -= shares * price
            self.shares += shares
            
        elif shares < 0:  # Sold shares (negative shares)
            self.money += abs(shares) * price
            self.shares -= abs(shares)
