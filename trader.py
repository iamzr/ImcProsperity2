from abc import ABC
from typing import List

import jsonpickle
import pandas as pd

from orders import Orders
from logger import Logger
from datamodel import Order, Symbol, TradingState
from rounds import round_1, round_3

logger = Logger()

class ITrader(ABC):
    def run(self, state: TradingState) -> dict[Symbol, List[Order]]:
        raise NotImplementedError()


class Trader(ITrader):
    def run(self, state: TradingState):
        traderData = jsonpickle.decode(state.traderData) if state.traderData else {}
        orders = Orders()

        round_1(state=state, traderData=traderData, orders=orders)
        round_3(state=state, traderData=traderData, orders=orders)
        
        # traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        traderData = jsonpickle.encode(traderData)
        conversions = 1

        logger.flush(state, orders.get_orders(), conversions, traderData)
        return orders.get_orders(), conversions, traderData
    
