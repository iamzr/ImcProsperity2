from abc import ABC
from typing import List

import jsonpickle
import pandas as pd

from orders import Orders
from logger import Logger
from datamodel import Order, OrderDepth, Symbol, TradingState
from rounds import round_1

logger = Logger()

class ITrader(ABC):
    def run(self, state: TradingState) -> dict[Symbol, List[Order]]:
        raise NotImplementedError()


def ema(price_history: list[float], span: int) -> int:
    """
    Method to calculate exponential moving average.

    :param span: the number of periods for the ema.
    """
    data_series = pd.Series(price_history[-span:])
    return int(data_series.ewm(span=span, adjust=False).mean().tail(1))

class Trader(ITrader):
    def run(self, state: TradingState):
        traderData = jsonpickle.decode(state.traderData) if state.traderData else {}
        orders = Orders()

        round_1(state=state, traderData=traderData, orders=orders)
        
        # traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        traderData = jsonpickle.encode(traderData)
        conversions = 1

        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        
        conversions = 1

        logger.flush(state, orders.get_orders(), conversions, traderData)
        return orders.get_orders(), conversions, traderData
