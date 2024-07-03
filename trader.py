from abc import ABC
from typing import List

import jsonpickle
import pandas as pd

# from datamodel import Order, Symbol, TradingState
from products import AMETHYSTS, STARFRUIT
from logger import Logger
from datamodel import Order, OrderDepth, Symbol, TradingState

logger = Logger()

class ITrader(ABC):
    def run(self, state: TradingState) -> dict[Symbol, List[Order]]:
        raise NotImplementedError()

def strategy_1(state: TradingState, product: Symbol, acceptable_bid_price: int, acceptable_ask_price: int) -> list[Order]:
    """
    Buys and sell product based on an acceptable price.
    """
    order_depth: OrderDepth = state.order_depths[product]
    orders: List[Order] = []
    print("Acceptable price : " + str(acceptable_ask_price))
    print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
    
    if len(order_depth.sell_orders) != 0:
        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
        if int(best_ask) < acceptable_ask_price:
            print("BUY", str(-best_ask_amount) + "x", best_ask)
            orders.append(Order(product, best_ask, -best_ask_amount))
    
    if len(order_depth.buy_orders) != 0:
        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
        if int(best_bid) > acceptable_bid_price:
            print("SELL", str(best_bid_amount) + "x", best_bid)
            orders.append(Order(product, best_bid, -best_bid_amount))
    
    return orders

def ema(price_history: list[float], span: int) -> int:
    """
    Method to calculate exponential moving average.

    :param span: the number of periods for the ema.
    """
    data_series = pd.Series(price_history[-span:])
    return int(data_series.ewm(span=span, adjust=False).mean().tail(1))


class Trader(ITrader):
    def run(self, state: TradingState):
        traderData: dict = jsonpickle.decode(state.traderData) if state.traderData else {}
        orders_to_make = {}

        # amethysts 
        acceptable_bid_price_amethysts = 10_000
        acceptable_ask_price_amethysts = 10_000

        orders_to_make[AMETHYSTS] = strategy_1(state=state, product=AMETHYSTS, acceptable_ask_price=acceptable_ask_price_amethysts, acceptable_bid_price=acceptable_bid_price_amethysts)

        # star fruit
        starfruit_span = 6
        if traderData.get("STARTFRUIT_PRICES"):
            price_of_startfruit = ema(traderData["STARTFRUIT_PRICES"], starfruit_span)

            orders_to_make[STARFRUIT] = strategy_1(state=state, product=STARFRUIT, acceptable_ask_price=price_of_startfruit, acceptable_bid_price=price_of_startfruit)

        
        starfruit_best_ask = min(state.order_depths[STARFRUIT].sell_orders)
        starfruit_best_bid = max(state.order_depths[STARFRUIT].buy_orders)
        starfruit_midprice = (starfruit_best_ask + starfruit_best_bid) / 2

        starfruit_prices = traderData.setdefault("STARTFRUIT_PRICES", [])
        if len(starfruit_prices) > starfruit_span:
            starfruit_prices.pop(0)
        
        starfruit_prices.append(starfruit_midprice)

        # traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        traderData = jsonpickle.encode(traderData)
        conversions = 1

        logger.flush(state, orders_to_make, conversions, traderData)
        return orders_to_make, conversions, traderData
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        
        conversions = 1

        logger.flush(state, orders_to_make, conversions, traderData)
        return orders_to_make, conversions, traderData