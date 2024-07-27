from abc import ABC, abstractmethod
from math import isclose
import pandas as pd
from datamodel import Order, OrderDepth, Symbol, TradingState
from orders import Orders
from products import CHOCOLATE, GIFT_BASKET, ROSES, STRAWBERRIES
from products import CHOCOLATE, ROSES, STRAWBERRIES
from math import exp, log, pi

def _ema(price_history: list[float], span: int) -> int:
    """
    Method to calculate exponential moving average.

    :param span: the number of periods for the ema.
    """
    data_series = pd.Series(price_history[-span:])
    return int(data_series.ewm(span=span, adjust=False).mean().tail(1))

def ema(state, trader_data, product: Symbol, span: int) -> int | None:
    key = f"{product}_PRICES"

    price = _ema(trader_data[key], span) if trader_data.get(key) else None

    mid_price = get_mid_price(state, product) 
    prices = trader_data.setdefault(key, [])

    if len(prices) > span:
        prices.pop(0)

    prices.append(mid_price)

    return price


def get_best_ask(state: TradingState, symbol: Symbol):
    order_depth = state.order_depths.get(symbol)

    if order_depth is None or len(order_depth.sell_orders) == 0:
        return None, None

    return list(order_depth.sell_orders.items())[0]

def get_best_bid(state: TradingState, symbol: Symbol):
    order_depth = state.order_depths.get(symbol)

    if order_depth is None or len(order_depth.buy_orders) == 0:
        return None, None

    return list(order_depth.buy_orders.items())[0]

def get_mid_price(state: TradingState, symbol: Symbol):
    best_ask, _ = get_best_ask(state, symbol)
    best_bid, _ = get_best_bid(state, symbol)

    if best_ask and best_bid:
        return (best_ask + best_bid) / 2
    
    return None

class Strategy(ABC):
    def __init__(self, state: TradingState, orders: Orders) -> None:
        self._state = state
        self._orders = orders

    @abstractmethod    
    def run():
        raise NotImplementedError()
        
    
class AcceptablePriceWithEmaStrategy(Strategy):
    def __init__(self, state: TradingState, orders: Orders, trader_data: dict, product: Symbol, span: int) -> None:
        super().__init__(state, orders)
        self._trading_data = trader_data
        self._product = product
        self._span = span
    
    def run(self):
        price = ema(self._state, self._trading_data, self._product, self._span)
        if price is None:
            return 

        s = AcceptablePriceStrategy(state=self._state, orders=self._orders, product=self._product, acceptable_ask_price=price, acceptable_bid_price=price)
        s.run()



class AcceptablePriceStrategy(Strategy):
    """
    Buys and sell product based on an acceptable price.
    """
    def __init__(self, state: TradingState, orders: Orders, product: Symbol, acceptable_bid_price: int, acceptable_ask_price: int) -> None:
        super().__init__(state, orders)
        self._product = product
        self._acceptable_bid_price = acceptable_bid_price
        self._acceptable_ask_price = acceptable_ask_price
    
    def run(self):
        print("Acceptable price : " + str(self._acceptable_ask_price))

        best_ask, best_ask_amount = get_best_ask(self._state, self._product) 
        if best_ask and best_ask_amount is not None:
            if int(best_ask) < self._acceptable_ask_price:
                self._orders.place_order(self._product, best_ask, -best_ask_amount)

        best_bid, best_bid_amount = get_best_bid(self._state, self._product)
        if best_bid and best_bid_amount is not None:
            if int(best_bid) > self._acceptable_bid_price:
                self._orders.place_order(self._product, best_bid, -best_bid_amount)

class SpreadTradingStrategy(Strategy):
    def __init__(self, state: TradingState, orders: Orders, portfolio_1: list[Symbol], portfolio_1_price: int, portfolio_2: list[Symbol], portfolio_2_price: int, spread_mean: float, spread_std: float, threshold: float) -> None:
        super().__init__(state, orders)

        self._portfolio_1 = portfolio_1
        self._portfolio_2 = portfolio_2
        self._portfolio_1_price = portfolio_1_price
        self._portfolio_2_price = portfolio_2_price
        self._spread_mean = spread_mean
        self._spread_std = spread_std
        self._threshold = threshold
    
    def run(self):
        spread = self._portfolio_1_price - self._portfolio_2_price 
        
        z_score = (spread - self._spread_mean) /self._spread_std 

        print(z_score)
        if z_score > self._threshold:
            for product in self._portfolio_1:
                best_bid, best_bid_amount = get_best_bid(self._state, product)
                self._orders.place_order(product, best_bid, -best_bid_amount)
        elif z_score < -self._threshold:
            for product in self._portfolio_1:
                best_ask, best_ask_amount = get_best_ask(self._state, product)
                self._orders.place_order(product ,best_ask, -best_ask_amount)

        elif isclose(z_score, 0.0, abs_tol=0.1):
            for product in self._portfolio_2:
                pos = self._state.position.get(product)

                if not pos:
                    continue

                if pos > 0:
                    best_bid, _ = get_best_bid(self._state, product)
                    self._orders.place_order(product, best_bid, -pos)
                elif pos < 0:
                    best_ask, _ = get_best_ask(self._state, product)
                    self._orders.place_order(product, best_ask, -pos)

class VanillaOptionsPricing():
    def _norm_cdf(self, x):
        """
        An approximation to the cumulative distribution
        function for the standard normal distribution:
        N(x) = \frac{1}{sqrt(2*\pi)} \int^x_{-\infty} e^{-\frac{1}{2}s^2} ds
        """
        k = 1.0/(1.0+0.2316419*x)
        k_sum = k * (0.319381530 + k * (-0.356563782 + \
            k * (1.781477937 + k * (-1.821255978 + 1.330274429 * k))))

        if x >= 0.0:
            return (1.0 - (1.0 / ((2 * pi)**0.5)) * exp(-0.5 * x * x) * k_sum)
        else:
            return 1.0 - self._norm_cdf(-x)

    def _norm_pdf(self, x):
        """
        Standard normal probability density function
        """
        return (1.0/((2*pi)**0.5))*exp(-0.5*x*x)

    def _d_j(self, j, S, K, r, v, T):
        """
        d_j = \frac{log(\frac{S}{K})+(r+(-1)^{j-1} \frac{1}{2}v^2)T}{v sqrt(T)}
        """
        return (log(S/K) + (r + ((-1)**(j-1))*0.5*v*v)*T)/(v*(T**0.5))

    def call_price(self, S, K, r, v, T):
        """
        Price of a European call option struck at K, with
        spot S, constant rate r, constant vol v (over the
        life of the option) and time to maturity T
        """
        return S * self._norm_cdf(self._d_j(1, S, K, r, v, T)) - \
            K*exp(-r*T) * self._norm_cdf(self._d_j(2, S, K, r, v, T))

    def put_price(self, S, K, r, v, T):
        """
        Price of a European put option struck at K, with
        spot S, constant rate r, constant vol v (over the
        life of the option) and time to maturity T
        """
        return -S * self._norm_cdf(-self._d_j(1, S, K, r, v, T)) + \
            K*exp(-r*T) * self._norm_cdf(-self._d_j(2, S, K, r, v, T))