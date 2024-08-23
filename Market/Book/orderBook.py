import sys
import math
from collections import deque
import numpy as np

from .orderTree import OrderTree


class OrderBook(object):
    def __init__(self, price_digits=3):
        self.tape = deque(maxlen=None)  # Index [0] is most recent trade
        self.bids = OrderTree()
        self.asks = OrderTree()
        self.lastTick = None
        self.lastTimestamp = 0
        self.price_digits = int(price_digits)
        self.time = 0
        self.nextQuoteID = 0
        self.trend = 0

### CHANGES ##########################################################################################
        self.last_6_prices = []
        self.volatility = 0
    
    def get_last_6_prices(self):
        return self.last_6_prices
    def set_last_6_prices(self,ls):
        self.last_6_prices = ls
        return
    
    def get_volatility(self):
        return self.volatility
    def get_time(self):
        return self.time
    def get_bids(self):
        return self.bids
    def get_asks(self):
        return self.asks
    def get_trades(self):
        return self.tape   
    def get_trend(self):
        return self.trend
    
    def get_order_by_idNum(self, idNum):
        if(type(self.bids.getOrder(idNum)) == dict):
            return self.bids.getOrder(idNum)
        elif(type(self.asks.getOrder(idNum)) == dict):
            return self.asks.getOrder(idNum)
        else:
            return
    
    def get_market_price(self):
        if(self.getBestAsk() == None or self.getBestBid() == None):
            return None
        else:
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
#Takes in a list of 6 prices and calculates if there's a price movement trend
    def update_price_movements(self):
        if(len(self.last_6_prices) < 6):
            self.trend = 0
            return
        else:
            up_count = 1
            down_count = -1
            trend_set = self.last_6_prices[0] - self.last_6_prices[1]

            for i in range(1, len(self.last_6_prices) - 1):
            #First price movement is positive
                next_move = self.last_6_prices[i] - self.last_6_prices[i+1]
                if(trend_set > 0):
                    if(next_move > 0):
                        up_count += 1
                    else:
                        self.trend = up_count
                        return 
            #First price movement is negative
                elif(trend_set < 0):
                    if(next_move < 0):
                        down_count -= 1
                    else:
                        self.trend = down_count
                        return
                else:
                    return
            if(up_count == 5):
                self.trend = up_count
                return
            elif(down_count == -5):
                self.trend = down_count
                return
            else:
                return
        
    def get_num_bids(self):
        qty = 0
        for price in self.bids.priceTree:
            order_list = self.bids.getPrice(price)
            for order in order_list:
                if order.agentID != 0:
                    qty += order.qty
        return qty

    def get_num_asks(self):
        qty = 0
        for price in self.asks.priceTree:
            order_list = self.asks.getPrice(price)
            for order in order_list:
                if order.agentID != 0:
                    qty += order.qty
        return qty 

#####################################################################################################

    def clipPrice(self, price):
        return int(round(price * 10 ** self.price_digits))

    def updateTime(self):
        self.time += 1

    def processOrder(self, quote, fromData, verbose):
        orderType = quote['type']
        orderInBook = None
        if fromData:
            self.time = quote['timestamp']
        else:
            self.updateTime()
            quote['timestamp'] = self.time
        if quote['qty'] <= 0:
            sys.exit('processLimitOrder() given order of qty <= 0')
        if not fromData:
            self.nextQuoteID += 1
        if orderType == 'limit':
            quote['price'] = self.clipPrice(quote['price'])
            trades, orderInBook = self.processLimitOrder(
                quote, fromData, verbose)
        else:
            sys.exit("processOrder() given neither 'market' nor 'limit'")
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
            counterparty_tran_id = headOrder.idNum
            counterpartyAgent = headOrder.agentID
            if qtyToTrade < headOrder.qty:
                tradedQty = qtyToTrade
                # Amend book order
                newBookQty = headOrder.qty - qtyToTrade
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
                        counterparty, quote['tid'], quote['agentID'])))
            transactionRecord = {'timestamp': self.time,
                                 'price': tradedPrice,
                                 'qty': tradedQty,
                                 'time': self.time} #'agentID': quote['agentID]
#### Side represents the matching limit order book order NOT the incoming order i.e. the most recent order will be an ask
            if side == 'bid':
                #Order that existed in order book
                transactionRecord['party1'] = [quote['agentID'],
                                               'ask']
                #Order that was submitted by trader
                transactionRecord['party2'] = [counterpartyAgent,
                                                'bid']
#### Side represents the matching limit order book order NOT the incoming order i.e. the most recent order will be a bid
            else:
                transactionRecord['party1'] = [quote['agentID'],
                                               'bid']
                transactionRecord['party2'] = [counterpartyAgent,
                                               'ask']
            self.tape.append(transactionRecord)
            trades.append(transactionRecord)
        return qtyToTrade, trades

    def processLimitOrder(self, quote, fromData, verbose):
        orderInBook = None
        trades = []
        qtyToTrade = quote['qty']
        side = quote['side']
        price = quote['price']
        if side == 'bid':
            while (self.asks and
                   price >= self.asks.minPrice() and
                   qtyToTrade > 0):
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

    def cancelOrder(self, side, idNum, time=None):
        if time:
            self.time = time
        else:
            self.updateTime()
        if side == 'bid':
            if self.bids.orderExists(idNum):
                self.bids.removeOrderById(idNum)
        elif side == 'ask':
            if self.asks.orderExists(idNum):
                self.asks.removeOrderById(idNum)
        else:
            sys.exit('cancelOrder() given neither bid nor ask')

    def modifyOrder(self, idNum, orderUpdate, time=None):
        if time:
            self.time = time
        else:
            self.updateTime()

        side = orderUpdate['side']
        orderUpdate['idNum'] = idNum
        orderUpdate['timestamp'] = self.time
        
        if side == 'bid':
            if self.bids.orderExists(orderUpdate['idNum']):
                self.bids.updateOrder(orderUpdate)
        elif side == 'ask':
            if self.asks.orderExists(orderUpdate['idNum']):
                self.asks.updateOrder(orderUpdate)
        else:
            sys.exit('modifyOrder() given neither bid nor ask')

    def getVolumeAtPrice(self, side, price):
        price = self.clipPrice(price)
        if side == 'bid':
            vol = 0
            if self.bids.priceExists(price):
                vol = self.bids.getPrice(price).volume
            return vol
        elif side == 'ask':
            vol = 0
            if self.asks.priceExists(price):
                vol = self.asks.getPrice(price).volume
            return vol
        else:
            sys.exit('getVolumeAtPrice() given neither bid nor ask')

    def getBestBid(self):
        return self.bids.maxPrice()

    def getWorstBid(self):
        return self.bids.minPrice()

    def getBestAsk(self):
        return self.asks.minPrice()

    def getWorstAsk(self):
        return self.asks.maxPrice()

    def tapeDump(self, fname, fmode, tmode):
        dumpfile = open(fname, fmode)
        for tapeitem in self.tape:
            dumpfile.write('%s, %s, %s\n' % (tapeitem['time'],
                                             tapeitem['price'],
                                             tapeitem['qty']))
        dumpfile.close()
        if tmode == 'wipe':
            self.tape = []

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