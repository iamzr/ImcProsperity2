from math import isclose
import pandas as pd
from datamodel import Order, OrderDepth, Symbol, TradingState
from orders import Orders
from products import CHOCOLATE, GIFT_BASKET, ROSES, STRAWBERRIES

def ema(price_history: list[float], span: int) -> int:
    """
    Method to calculate exponential moving average.

    :param span: the number of periods for the ema.
    """
    data_series = pd.Series(price_history[-span:])
    return int(data_series.ewm(span=span, adjust=False).mean().tail(1))

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

def pairs_trading(state: TradingState, orders: Orders, combined_product, component_products):
    products = [combined_product]
    products.extend(component_products)

    best_asks = {}
    best_bids = {}
    mid_price = {}

    for product in products:
        order_depth: OrderDepth = state.order_depths.get(product)
        if not order_depth:
            return

        best_asks[product] = list(order_depth.sell_orders.items())[0]
        best_bids[product] = list(order_depth.buy_orders.items())[0]
        mid_price[product] = (best_asks[product][0] + best_bids[product][0]) / 2

    
    predicted_price = get_gift_basket_price(mid_price[CHOCOLATE], mid_price[ROSES], mid_price[STRAWBERRIES])

    spread = mid_price[GIFT_BASKET] - predicted_price

    SPREAD_MEAN = 376.0862
    SPREAD_STD = 76.354
    z_score = (spread - SPREAD_MEAN) / SPREAD_STD

    print(z_score)

    threshold = 1.645

    if z_score > threshold:
        orders.place_order(GIFT_BASKET,best_asks[product][0], best_asks[product][1])
    elif z_score < -threshold:
        orders.place_order(GIFT_BASKET,best_bids[product][0], best_asks[product][1])
    elif z_score == 0:
        pos = state.position[GIFT_BASKET]
        if pos > 0:
            orders.place_order(GIFT_BASKET,best_bids[product][0], -pos)
        elif pos < 0:
            orders.place_order(GIFT_BASKET,best_asks[product][0], -pos)



    

def get_gift_basket_price(chocolate, roses, strawberries):
    return 4 * chocolate + roses + 6 * strawberries

def round_3_arbitrage(state, orders: Orders, combined_product, component_products):
    products = [combined_product]
    products.extend(component_products)

    best_asks = {}
    best_bids = {}

    for product in products:
        order_depth: OrderDepth = state.order_depths.get(product)
        if not order_depth:
            return

        best_asks[product] = list(order_depth.sell_orders.items())[0]
        best_bids[product] = list(order_depth.buy_orders.items())[0]

    lowest_asks_of_components = 4* best_asks[CHOCOLATE][0] + 6* best_asks[STRAWBERRIES][0] + best_asks[ROSES][0]
    highest_bid_of_combined = best_bids[combined_product][0]

    i = 0
    print("best asks", best_asks)
    print("best bids", best_bids)
    while True:
        if 4 * i >= best_asks[CHOCOLATE][1] or 6 * i >=best_asks[STRAWBERRIES][1] or i >= best_asks[ROSES][1] or i >= best_bids[combined_product][1]:
            break
        i += 1

    amount = i

    if lowest_asks_of_components < highest_bid_of_combined:
        # place buy orders for components at lowest asks
        for product in component_products:
            orders.place_order(product, best_asks[product][0], -amount)

        # place sell orders for combined at highest bid
        orders.place_order(product, best_bids[combined_product][0], amount)

    # lowest_asks_of_combined = best_asks[combined_product][0]
    # highest_bid_of_components = sum(best_bids[product][0] for product in component_products)


    # if lowest_asks_of_combined < highest_bid_of_components:
    #     for product in component_products:
    #         print("SELL", str(-best_bids[product][1]) + "x", best_bids[product])
    #         orders_to_make.setdefault(product, []).append(Order(product, best_bids[product][0], -best_bids[product][1]))

    #     # place sell orders for combined at highest bid
    #     print("BUY", str(best_asks[combined_product][1]) + "x", best_asks[product])
    #     orders_to_make.setdefault(product, []).append(Order(product, best_asks[combined_product][0], -best_asks[combined_product][1]))


