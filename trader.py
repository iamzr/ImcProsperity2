from abc import ABC
from typing import List

# from datamodel import Order, Symbol, TradingState
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState

import json
from typing import Any


class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        print(json.dumps([
            self.compress_state(state),
            self.compress_orders(orders),
            conversions,
            trader_data,
            self.logs,
        ], cls=ProsperityEncoder, separators=(",", ":")))

        self.logs = ""

    def compress_state(self, state: TradingState) -> list[Any]:
        return [
            state.timestamp,
            state.traderData,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing["symbol"], listing["product"], listing["denomination"]])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.price,
                    trade.quantity,
                    trade.buyer,
                    trade.seller,
                    trade.timestamp,
                ])

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sunlight,
                observation.humidity,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

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

        logger.flush(state, {AMETHYSTS: orders_to_make}, None, None)
        return {AMETHYSTS: orders_to_make}, None, None