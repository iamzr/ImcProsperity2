from datamodel import Symbol, TradingState
from orders import Orders


def acceptable_price_strategy(state: TradingState, orders: Orders, product: Symbol, acceptable_bid_price: int, acceptable_ask_price: int):
    """
    Buys and sell product based on an acceptable price.
    """
    order_depth = state.order_depths.get(product)

    if order_depth is None:
        return

    print("Acceptable price : " + str(acceptable_ask_price))
    print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

    if len(order_depth.sell_orders) != 0:
        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
        if int(best_ask) < acceptable_ask_price:
            orders.place_order(product, best_ask, -best_ask_amount)

    if len(order_depth.buy_orders) != 0:
        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
        if int(best_bid) > acceptable_bid_price:
            print("SELL", str(best_bid_amount) + "x", best_bid)
            orders.place_order(product, best_bid, -best_bid_amount)