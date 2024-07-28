from abc import ABC
from typing import List

import jsonpickle
import pandas as pd

from orders import Orders
from logger import Logger
from datamodel import Order, Symbol, TradingState
from rounds import Round1, Round3, Round4

logger = Logger()

class Trader:
    def run(self, state: TradingState):
        traderData = jsonpickle.decode(state.traderData) if state.traderData else {}
        orders = Orders()

        Round1(state=state, traderData=traderData, orders=orders).run() # type: ignore
        Round3(state=state, traderData=traderData, orders=orders).run() # type: ignore
        Round4(state=state, traderData=traderData, orders=orders).run() # type: ignore
        
        # traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        traderData = jsonpickle.encode(traderData)
        conversions = 1

        logger.flush(state, orders.get_orders(), conversions, traderData) # type: ignore
        return orders.get_orders(), conversions, traderData
    
