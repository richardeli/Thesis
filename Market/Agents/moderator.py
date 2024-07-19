import numpy as np
import random
import math

class Moderator():
    def __init__(self):
        """
        Initializes the Fundamentalist agent.

        Args:
            agentID (int): Unique identifier for the agent.
            initial_cash (float): Initial cash balance of the agent.
        """
        self.money = 0
        self.agentID = 0
        self.shares = 0
        self.type = "Moderator"

    """ GETTER AND SETTER METHODS"""
    def get_agentID(self):
        return self.agentID

    def set_shares(self, new_shares):
        self.shares = new_shares
        return

    def get_shares(self):
        return self.shares

    def add_share(self, share):
        self.shares += share
        return
    
    def settle_trade(self, price, shares):
        if shares > 0:  # Bought shares (positive shares)
            self.shares += shares
            
        elif shares < 0:  # Sold shares (negative shares)
            self.shares -= abs(shares)