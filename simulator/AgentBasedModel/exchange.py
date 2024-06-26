from typing import Type

import matplotlib.pyplot as plt 

from AgentBasedModel.utils import Order, OrderList
from AgentBasedModel.utils.math import exp
import AgentBasedModel.settings as settings
import random



class Asset:
    id = 0

    def __init__(self):
        self.type = 'Stock'
        self.name = f'Asset{self.id}'
        self.id = Asset.id
        Asset.id += 1

    def update(self):
        pass


class Stock(Asset):
    """
    Asset with the following properties:
    - Dividend is paid to holdersxs
    - Dividend is non-negative
    - Dividend changes over time
    - Traded throught ExchangeAgent
    """
    def __init__(self, dividend: float):
        """
        :param dividend: initial dividend > 0
        """
        super().__init__()
        self.type = 'Stock'
        self.dividend = dividend
        
        self.dividend_book = list()  # act like queue
        self._fill_book()
    
    def _next_dividend(self, div_current: float, std: float = 5e-3) -> float :

        random.seed(settings.seed)

        settings.seed +=1 
        
        x = max(exp(random.normalvariate(0, std)), 0)
        return div_current * x

    def _fill_book(self, n: int = 100):
        """
        Fill fill dividend book with future dividends.
        
        :param n: number of dividends to fill
        """
        if not self.dividend_book:
            self.dividend_book.append(self.dividend)
            n -= 1
        
        for i in range(n):
            div = self.dividend_book[-1]
            div = self._next_dividend(div)
            self.dividend_book.append(div)
    
    def update(self):
        """
        Add new dividend to queue and pop last
        """
        self._fill_book(1)
        self.dividend = self.dividend_book.pop(0)


class ExchangeAgent:
    """
    ExchangeAgent implements automatic orders handling within the order book
    """
    id = 0

    def __init__(
            self,
            asset: Type[Asset],                                             # traded asset
            risk_free_rate: float = 5e-4, transaction_cost: float = 0,      # economy rates
            mean: float = None, std: float = 25, n: int = 1000, # order book initialization
        ):
        """Creates ExchangeAgent with initialised order book and future dividends

        :param price: stock initial price
        :param std: standard deviation of order prices
        :param n: number of orders initialised
        :param rf: risk-free rate
        :param transaction_cost: transaction cost on operations for traders (fraction)
        """
        if mean is None:
            mean = asset.dividend / risk_free_rate

        self.name = f'Exchange{self.id}'
        self.id = ExchangeAgent.id
        ExchangeAgent.id += 1

        self.asset = asset
        self.risk_free_rate = risk_free_rate
        self.transaction_cost = transaction_cost

        self.order_book = self.order_book = {'bid': OrderList('bid'), 'ask': OrderList('ask')}
        self._fill_book(mean, std, n)

        self.ask_volume = 0.0
        self.bid_volume = 0.0

        #print_book_values(self.order_book)

    def _fill_book(self, mean: float, std: float , n: int):
        """Fill order book with random orders.

        Generate prices from normal distribution with *std*, and *price* as center; generate
        quantities for these orders from uniform distribution with 1, 5 bounds. Set bid orders when
        order price is less than *price*, set ask orders when order price is greater than *price*.
        """

        random.seed(settings.seed)

        settings.seed +=1     

        prices1 = [round(random.normalvariate(mean - std, std), 1) for _ in range(n // 2)]
        prices2 = [round(random.normalvariate(mean + std, std), 1) for _ in range(n // 2)]
        quantities = [random.randint(1, 5) for _ in range(n)]

        for (p, q) in zip(sorted(prices1 + prices2), quantities):
            if p > mean:
                order = Order(round(p, 1), q, 'ask', None)
                self.order_book['ask'].append(order)
            else:
                order = Order(p, q, 'bid', None)
                self.order_book['bid'].push(order)

    def _clear_book(self):
        """
        **(UNUSED)** Clear order book from orders with 0 quantity.
        """
        self.order_book['bid'] = OrderList.from_list([order for order in self.order_book['bid'] if order.qty > 0])
        self.order_book['ask'] = OrderList.from_list([order for order in self.order_book['ask'] if order.qty > 0])

    def spread(self) -> dict:
        """
        Returns best bid and ask prices as dictionary

        :return: {'bid': float, 'ask': float}
        """
        if self.order_book['bid'] and self.order_book['ask']:
            return {'bid': self.order_book['bid'].first.price, 'ask': self.order_book['ask'].first.price}
        raise Exception(f'{self.name}: There no either bid | ask orders')

    def spread_volume(self) -> dict:
        """
        **(UNUSED)** Returns best bid and ask volumes as dictionary

        :return: {'bid': float, 'ask': float}
        """
        if self.order_book['bid'] and self.order_book['ask']:
            return {'bid': self.order_book['bid'].first.qty, 'ask': self.order_book['ask'].first.qty}
        raise Exception(f'There no either bid or ask orders')

    def spread_volume_best(self, value : int) -> dict:
        """
        Returns for first values best bid ans ask volumes as dictionary
        
        :return: {'bid': float, 'ask': float}
        """
        if len(self.order_book['bid']) >= value and len(self.order_book['ask']) >= value:
            bid_sum, ask_sum = 0.0, 0.0
            for i, item in enumerate(self.order_book['bid']):
                if i == value:
                    break
                bid_sum += item.qty

            for i, item in enumerate(self.order_book['ask']):
                if i == value:
                    break
                ask_sum += item.qty

            return {'bid': bid_sum, 'ask': ask_sum}
        raise Exception(f'There no either bid or ask orders')

    def price(self) -> float:
        """
        Returns current stock price as mean between best bid and ask prices
        """
        spread = self.spread()
        if spread:
            return round((spread['bid'] + spread['ask']) / 2, 5)
        raise Exception(f'Price cannot be determined, since no orders either bid or ask')

    def dividend(self, access: int = None) -> list :
        """
        :param access:
        - **None:** return float or int (current dividend)
        - **0:** return list of dividends (only current dividend)
        - **int > 0:** return list of dividends (current dividend and n future)

        :returns: either
        - **for stocks:** current dividend or *access* future dividends (if called by trader).
        - **for others:** returns 0.
        """
        if self.asset.type != 'Stock':
            return 0
        if access is None:  # both None and 0 (see Fundamentalist __init__)
            return self.asset.dividend
        return [self.asset.dividend, *self.asset.dividend_book[:access]]

    def limit_order(self, order: Order):
        bid, ask = self.spread().values()
        t_cost = self.transaction_cost
        if not bid or not ask:
            return
        if not order.qty:
            return

        if order.order_type == 'bid':
            if order.price >= ask:
                order = self.order_book['ask'].fulfill(order, t_cost)
            if order.qty > 0:
                self.order_book['bid'].insert(order)
            self.bid_volume += order.qty
            return

        elif order.order_type == 'ask':
            if order.price <= bid:
                order = self.order_book['bid'].fulfill(order, t_cost)
            if order.qty > 0:
                self.order_book['ask'].insert(order)
            
            self.ask_volume += order.qty

    def market_order(self, order: Order) -> Order:
        t_cost = self.transaction_cost
        if not order.qty:
            return order
        
        if order.order_type == 'bid':
            order = self.order_book['ask'].fulfill(order, t_cost)
            #self.bid_volume += order.qty
        elif order.order_type == 'ask':
            order = self.order_book['bid'].fulfill(order, t_cost)
            #self.ask_volume += order.qty
        return order

    def cancel_order(self, order: Order):
        if order.order_type == 'bid':
            self.order_book['bid'].remove(order)
            self.bid_volume -= order.qty
        elif order.order_type == 'ask':
            self.order_book['ask'].remove(order)
            self.ask_volume -= order.qty
    
    def clear_traded_volume(self):
        self.ask_volume = 0.0
        self.bid_volume = 0.0




       

