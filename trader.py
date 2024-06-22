from abc import ABC
from typing import List

from datamodel import Order, Symbol, TradingState

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

        orders_to_make = []


        amethsts_orders = state.order_depths.get(AMETHYSTS)
        
        if not amethsts_orders:
            return

        current_position = state.position[AMETHYSTS] if state.position.get(AMETHYSTS) else 0

        # buy low
        # if ask price is less than or equal to 9994, submit buy order
        sell_orders =  amethsts_orders.sell_orders

        sell_prices = list(sell_orders.keys())
        sell_prices.sort()

        for sell_price in sell_prices:
            # for prices less than or equal to 9994 it makes sense to buy them if people are selling
            if sell_price <= 9994:
                #create order

                # calcaulate quatitiy you want to buy based on current position
                sell_quantity = sell_orders[sell_price]

                if abs(current_position) + sell_quantity > POSITION_LIMITS[AMETHYSTS]:
                    break

                state.position[AMETHYSTS] = current_position +  sell_quantity # sell quantity is negative
                
                order = Order(
                    symbol=AMETHYSTS,
                    price=sell_price,
                    quantity=sell_quantity
                )

                orders_to_make.append(order)


        # sell high,
        # if ask price is greater to equal to 1004 sell
        bid_orders = amethsts_orders.buy_orders
        bid_prices = list(bid_orders.keys())
        bid_prices.sort()

        for bid_price in bid_prices:
            # for prices less than or equal to 9994 it makes sense to buy them if people are selling
            if bid_price <= 10004:
                #create order

                # calcaulate quatitiy you want to buy based on current position
                buy_quantity = bid_orders[bid_price]

                if abs(current_position) + buy_quantity > POSITION_LIMITS[AMETHYSTS]:
                    break

                state.position[AMETHYSTS] = current_position + buy_quantity # sell quantity is negative
                
                order = Order(
                    symbol=AMETHYSTS,
                    price=bid_price,
                    quantity=buy_quantity
                )

                orders_to_make.append(order)

        return {AMETHYSTS: orders_to_make}, None, None