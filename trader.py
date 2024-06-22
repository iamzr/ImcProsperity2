from abc import ABC
from typing import List

# from datamodel import Order, Symbol, TradingState
from logger import Logger
from datamodel import Order, Symbol, TradingState



logger = Logger()

AMETHYSTS: Symbol = "AMETHYSTS"
STARFRUIT: Symbol = "STARFRUIT"

POSITION_LIMITS = {
    AMETHYSTS : 20,
    STARFRUIT : 20,
}

class ITrader(ABC):
    def run(self, state: TradingState) -> dict[Symbol, List[Order]]:
        raise NotImplementedError()


class Trader(ITrader):
    def run(self, state: TradingState):

        orders_to_make = {}


        amethsts_orders = state.order_depths.get(AMETHYSTS)
        
        if not amethsts_orders:
            return

        current_position = state.position.get(AMETHYSTS, 0)

        # buy low
        # if ask price is less than or equal to 9994, submit buy order
        sell_orders =  amethsts_orders.sell_orders

        # not we assume that the ask prices are already sorted in the dictionary
        for ask_price, sell_quantity in sell_orders.items():
            # for prices less than or equal to 9994 it makes sense to buy them if people are selling
            if ask_price < 10_000:

                #create order

                # calcaulate quatitiy you want to buy based on current position
                if abs(current_position + sell_quantity) > POSITION_LIMITS[AMETHYSTS]:
                    break

                current_position =+ sell_quantity # sell quantity is negative
                
                print("BUY", str(-sell_quantity) + "x", ask_price)
                order = Order(
                    symbol=AMETHYSTS,
                    price=ask_price,
                    quantity=-sell_quantity
                )

                orders_to_make.setdefault(AMETHYSTS, []).append(order)


        # sell high,
        # if ask price is greater to equal to 1004 sell
        buy_orders = amethsts_orders.buy_orders

        # assuming the buy orders are already sorted 
        for bid_price, buy_quantity in buy_orders.items():
            # for prices greater than or equal to 10004 it makes sense to sell them if people are buying
            if bid_price > 10_000:
                #create order

                # calcaulate quatitiy you want to buy based on current position
                if abs(current_position + buy_quantity) > POSITION_LIMITS[AMETHYSTS]:
                    break

                current_position =+ buy_quantity                 

                print("SELL", str(buy_quantity) + "x", bid_price)
                order = Order(
                    symbol=AMETHYSTS,
                    price=bid_price,
                    quantity=-buy_quantity
                )

                orders_to_make.setdefault(AMETHYSTS, []).append(order)


        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        
        conversions = 1

        logger.flush(state, orders_to_make, conversions, traderData)
        return orders_to_make, conversions, traderData