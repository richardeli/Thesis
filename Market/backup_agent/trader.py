from Book import order

class Trader():
    def __init__(self, agent_ID, money):
        self.money = money
        self.agent_ID = agent_ID
    
    def getMoney(self):
        return self.money
    
    def setMoney(self, money):
        self.money = money
        return
    
    def getAgentID(self):
        return self.agent_ID
    
    def setAgentID(self, new_ID):
        self.agent_ID = new_ID
        return

#    def getLimitOrderBookState(LOB):
#        self.limitOrderBook = None

    def strategise(self):
        #logic

        #check if previous sell order is +- 20% of sell price, if yes then cancel order to get money back
        #cancel_order

        #check if money available
        
        #decide strategy, buy order (market, limit), sell order(limit), do nothing
        
        ######### Speculator ##########
        #buy order logic
            ##if current market price in past 15 seconds price has increased by random.random percentage between 10 - 20 and money is 0 then buy
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

    #If type is true then market order
    def buy_order(self, type, quantity, price, tid):
        if(type == True):
            quote = {'type': 'market',
                    'side': 'bid',
                    'qty': quantity,
                    'price': price,
                    'tid': tid},
        else: 
            quote = {'type': 'limit',
                    'side': 'bid',
                    'qty': quantity,
                    'price': price,
                    'tid': tid},
        return quote

    def sell_order(self, quantity, price, tid):
        quote = {'type': 'limit',
                'side': 'ask',
                'qty': quantity,
                'price': price,
                'tid': tid},
        return quote
    
    def cancel_order(self):
        #remove limit order book order
        return
        
    def trade(self):
        action = False
        buy = False
        #logic --> if trade then  set action to true
        #define parameters: quantity, price, tid,, type
        
        if(action == True):
            if(buy == True):
                self.buy_order()
            else:
                self.sell_order()
        else:
            print("he")

        return