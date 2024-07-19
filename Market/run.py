from Book.orderBook import OrderBook

import numpy as np
import random

def test_book():

    # Create a LOB object
    market = OrderBook()

    ########### Limit Orders #############
    # Create some limit orders
    someOrders = [{'type': 'limit',
                   'side': 'ask',
                   'qty': 5,
                   'price': 101,
                   'tid': 100},
                  {'type': 'limit',
                   'side': 'ask',
                   'qty': 5,
                   'price': 103,
                   'tid': 101},
                  {'type': 'limit',
                   'side': 'ask',
                   'qty': 5,
                   'price': 105,
                   'tid': 102},
                  {'type': 'limit',
                   'side': 'ask',
                   'qty': 5,
                   'price': 110,
                   'tid': 103},
                  {'type': 'limit',
                   'side': 'ask',
                   'qty': 5,
                   'price': 104,
                   'tid': 103},
                  {'type': 'limit',
                   'side': 'ask',
                   'qty': 5,
                   'price': 109,
                   'tid': 103},
                   {'type': 'limit',
                   'side': 'ask',
                   'qty': 5,
                   'price': 106,
                   'tid': 103},
                   {'type': 'limit',
                   'side': 'ask',
                   'qty': 5,
                   'price': 107,
                   'tid': 107},
                  {'type': 'limit',
                   'side': 'bid',
                   'qty': 5,
                   'price': 99,
                   'tid': 100},
                  {'type': 'limit',
                   'side': 'bid',
                   'qty': 5,
                   'price': 98,
                   'tid': 101},
                  {'type': 'limit',
                   'side': 'bid',
                   'qty': 5,
                   'price': 99,
                   'tid': 102},
                  {'type': 'limit',
                   'side': 'bid',
                   'qty': 5,
                   'price': 97,
                   'tid': 103},
                  {'type': 'limit',
                   'side': 'bid',
                   'qty': 5,
                   'price': 96,
                   'tid': 100},
                  {'type': 'limit',
                   'side': 'bid',
                   'qty': 5,
                   'price': 95,
                   'tid': 101},
                  {'type': 'limit',
                   'side': 'bid',
                   'qty': 5,
                   'price': 94,
                   'tid': 102},
                  {'type': 'limit',
                   'side': 'bid',
                   'qty': 5,
                   'price': 93,
                   'tid': 103},
                  ]

    # Add orders to LOB instantiate market orders
    for order in someOrders:
        trades, idNum = market.processOrder(order, False, False)
    
if __name__ == '__main__':
    test_book()