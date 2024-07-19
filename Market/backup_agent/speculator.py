from trader import Trader
import random

#Price = 101000 || 101,000
class Speculator(Trader):
    def __init__(self, agentID, money):
        super().__init__(agentID, money)

        ###### Check math on this ########
        self.volatility_threshold = random.randint(0, 20)
        self.spread = random.randint(1,10)
        self.money = money
    
    def strategise(self, orderBook):
        # logic

        #check if previous sell order is +- 20% of sell price, if yes then cancel order to get money back
        #cancel_order

        if(self.volatility_threshold >= abs(orderBook.get_volatility())):
            order =  {"type" : "market",
                        "side": "bid",
                        "qty" : 7}
            
        #check if money available
        
        #decide strategy, buy order (market, limit), sell order(limit), do nothing
        
        ######### Speculator ##########
        #buy order logic
            ##if current market price in past 15 seconds price has increased by random.random percentage between 10 - 20 and money is not 0 then buy
                ###and bid-ask spread is less than random . random between 1 - 5 then market
            ##else limit order
        
        #sell order logic
            ##if current market price in past 15 seconds price has decreased by random.random percentage between 10 - 20 and money is 0 then sell
                ###and bid-ask spread is less than random.random between 1-5 then market
        
        #else do nothing

        #if strategy = yes then:
            #return quote:
        #else:
        return
