import sys
import math
from collections import deque
import numpy as np

from .orderTree import OrderTree

class OrderBook(object):
    def __init__(self, price_digits=3):
        self.tape = deque(maxlen=None) 
        self.bids = OrderTree()
        self.asks = OrderTree()
        self.lastTick = None
        self.lastTimestamp = 0
        self.price_digits = int(price_digits)
        self.time = 0
        self.nextQuoteID = 0

        self.last_6_prices = []
        self.volatility = 0
        self.market_price = 0

#Clear Books
    def clear_books(self):
        self.bids.clear()
        self.asks.clear()
        return
    
#Get Set Bids
    def getBestBid(self):
        return self.bids.maxPrice()
    def getWorstBid(self):
        return self.bids.minPrice()

#Get Set Asks
    def getBestAsk(self):
        return self.asks.minPrice()
    def getWorstAsk(self):
        return self.asks.maxPrice()

#Get set market price
    def get_market_price(self):
        return self.market_price
    def set_market_price(self):
        self.market_price = (self.getBestBid() + self.getWorstAsk()) / 2
        return self.market_price

#Get set bids book
    def get_bids(self):
        return self.bids
    def set_bids(self, new_bids):
        self.bids = new_bids
        return self.bids

#Get set asks book
    def get_asks(self):
        return self.asks
    def set_asks(self, new_asks):
        self.asks = new_asks
        return self.asks

#Get set last 6 prices
    def get_last_6_prices(self):
        return self.last_6_prices
    def set_last_6_prices(self,ls):
        self.last_6_prices = ls
        return

#Get set volatility
    def get_volatility(self):
        return self.volatility
    def get_market_price(self):
        mkt_price = (self.getBestAsk() + self.getBestBid()) / 2
        return mkt_price
    
# update most recent price movement
# store the last 6 prices to calculate the most recent 5 price movements
# most recent value is at index 0
    def update_last_6_prices(self):
        if(self.getBestAsk() != None and self.getBestBid() != None):
            mkt_price = self.get_market_price()
            if(len(self.last_6_prices) == 6):
                self.last_6_prices = np.roll(self.last_6_prices, 1)
                self.last_6_prices[0] = mkt_price
            else:
                self.last_6_prices.insert(0, mkt_price)
            self.update_price_movements()            
        return

#Returns a decimal (0 - 100) that represents the % change over the last 5 movements
#Takes in a list of 6 prices and calcaultes the price movement of the last 5 
    def update_price_movements(self):
        if(len(self.last_6_prices) < 6):
            return 0
        else:
            temp_movement = []
            i=0
            while(i < len(self.last_6_prices) - 1):
                price_move = (self.last_6_prices[i]/self.last_6_prices[i+1]) - 1
                temp_movement.append(price_move)
                i += 1
            self.volatility = sum(temp_movement) / len(temp_movement)
        return

# #add Orders to bids or asks depending on order type
#     def addOrderToBook(self, order):
#         if(type(order) == dict):
#             f_order_type = order['type']

#             if(f_order_type == "bid"):
#                 self.bids["price"].append(order)
#             else:
#                 self.asks["price"].append(order)

#Bid and asks for the round are sorted now matching buyers and sellers

#####
    def clipPrice(self, price):
        return int(round(price * 10 ** self.price_digits))

    def updateTime(self):
        self.time += 1
    def get_time(self):
        return self.time

    def processOrder(self, order, fromData, verbose):
        if(type(order) != dict):
            return
        orderInBook = None
        
        if fromData:
            self.time = order['timestamp']
        else:
            self.updateTime()
            order['timestamp'] = self.time
#Error check
        if order['qty'] <= 0:
            sys.exit('processLimitOrder() given order of qty <= 0')
#Process order
        order['price'] = self.clipPrice(order['price'])
#1#######################################################################
        print(order)
        trades, orderInBook = self.processLimitOrder(
            order, fromData, verbose)
        self.update_last_6_prices()
        return trades, orderInBook

    def processOrderList(self, side, orderlist,
                         qtyStillToTrade, quote, verbose):
        '''
        Takes an order list (stack of orders at one price) and
        an incoming order and matches appropriate trades given
        the orders quantity.
        '''
        trades = []
        qtyToTrade = qtyStillToTrade
        while len(orderlist) > 0 and qtyToTrade > 0:
            headOrder = orderlist.getHeadOrder()
            tradedPrice = headOrder.price
            counterparty = headOrder.tid
            if qtyToTrade < headOrder.qty:
                tradedQty = qtyToTrade
                # Amend book order
                newBookQty = headOrder.qty - qtyToTrade
#3#######################################################################
                headOrder.updateQty(newBookQty, headOrder.timestamp)
                # Incoming done with
                qtyToTrade = 0
            elif qtyToTrade == headOrder.qty:
                tradedQty = qtyToTrade
                if side == 'bid':
                    # Hit the bid
                    self.bids.removeOrderById(headOrder.idNum)
                else:
                    # Lift the ask
                    self.asks.removeOrderById(headOrder.idNum)
                # Incoming done with
                qtyToTrade = 0
            else:
                tradedQty = headOrder.qty
                if side == 'bid':
                    # Hit the bid
                    self.bids.removeOrderById(headOrder.idNum)
                else:
                    # Lift the ask
                    self.asks.removeOrderById(headOrder.idNum)
                # We need to keep eating into volume at this price
                qtyToTrade -= tradedQty
            if verbose:
                print(('>>> TRADE \nt=%d $%f n=%d p1=%d p2=%d' %
                       (self.time, tradedPrice, tradedQty,
                        counterparty, quote['tid'])))

            transactionRecord = {'timestamp': self.time,
                                 'price': tradedPrice,
                                 'qty': tradedQty,
                                 'time': self.time}
            if side == 'bid':
                transactionRecord['party1'] = [counterparty,
                                               'bid',
                                               headOrder.idNum]
                transactionRecord['party2'] = [quote['tid'],
                                               'ask',
                                               None]
            else:
                transactionRecord['party1'] = [counterparty,
                                               'ask',
                                               headOrder.idNum]
                transactionRecord['party2'] = [quote['tid'],
                                               'bid',
                                               None]
            self.tape.append(transactionRecord)
            trades.append(transactionRecord)
        return qtyToTrade, trades

    def processLimitOrder(self, quote, fromData, verbose):
        orderInBook = None
        trades = []
        qtyToTrade = quote['qty']
        side = quote['type']
        price = quote['price']
        if side == 'bid':
            while (self.asks and
                   price >= self.asks.minPrice() and
                   qtyToTrade > 0):
#2#######################################################################s
                bestPriceAsks = self.asks.minPriceList()
                qtyToTrade, newTrades = self.processOrderList('ask',
                                                              bestPriceAsks,
                                                              qtyToTrade,
                                                              quote, verbose)
                trades += newTrades
            # If volume remains, add to book
            if qtyToTrade > 0:
                if not fromData:
                    quote['idNum'] = self.nextQuoteID
                quote['qty'] = qtyToTrade
                self.bids.insertOrder(quote)
                orderInBook = quote
        elif side == 'ask':
            while (self.bids and
                   price <= self.bids.maxPrice() and
                   qtyToTrade > 0):
                bestPriceBids = self.bids.maxPriceList()
                qtyToTrade, newTrades = self.processOrderList('bid',
                                                              bestPriceBids,
                                                              qtyToTrade,
                                                              quote, verbose)
                trades += newTrades
            # If volume remains, add to book
            if qtyToTrade > 0:
                if not fromData:
                    quote['idNum'] = self.nextQuoteID
                quote['qty'] = qtyToTrade
                self.asks.insertOrder(quote)
                orderInBook = quote
        else:
            sys.exit('processLimitOrder() given neither bid nor ask')
        return trades, orderInBook


    def __str__(self):
        result = ["------ Bids -------"]
        if self.bids is not None and len(self.bids) > 0:
            result.extend(str(v) for v in
                          self.bids.priceTree.values(reverse=True))
        result.append("------ Asks -------")
        if self.asks is not None and len(self.asks) > 0:
            result.extend(str(v) for v in
                          self.asks.priceTree.values(reverse=True))
        result.append("------ Trades ------")
        if self.tape is not None and len(self.tape) > 0:
            num = 0
            for entry in self.tape:
                if num < 5:
                    result.append(str(entry['qty']) + " @ " +
                                  str(entry['price']) +
                                  " (" + str(entry['timestamp']) + ")")
                    num += 1
                else:
                    break

        return '\n'.join(result)