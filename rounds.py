from datamodel import TradingState
from orders import Orders
from products import AMETHYSTS, CHOCOLATE, GIFT_BASKET, ROSES, STARFRUIT, STRAWBERRIES
from strategies import acceptable_price_strategy
from trader import arbitrage, ema


def round_1(state: TradingState, traderData: dict, orders: Orders):
    # amethysts 
    acceptable_bid_price_amethysts = 10_000
    acceptable_ask_price_amethysts = 10_000

    acceptable_price_strategy(state=state, orders=orders, product=AMETHYSTS, acceptable_ask_price=acceptable_ask_price_amethysts, acceptable_bid_price=acceptable_bid_price_amethysts)

    # star fruit
    starfruit_span = 6
    if traderData.get("STARTFRUIT_PRICES"):
        price_of_startfruit = ema(traderData["STARTFRUIT_PRICES"], starfruit_span)

        acceptable_price_strategy(state=state, orders=orders, product=STARFRUIT, acceptable_ask_price=price_of_startfruit, acceptable_bid_price=price_of_startfruit)


    starfruit_best_ask = min(state.order_depths[STARFRUIT].sell_orders)
    starfruit_best_bid = max(state.order_depths[STARFRUIT].buy_orders)
    starfruit_midprice = (starfruit_best_ask + starfruit_best_bid) / 2

    starfruit_prices = traderData.setdefault("STARTFRUIT_PRICES", [])
    if len(starfruit_prices) > starfruit_span:
        starfruit_prices.pop(0)

    starfruit_prices.append(starfruit_midprice)


def round_3(state: TradingState, traderData: dict, orders_to_make: dict):
    component_products = [CHOCOLATE, STRAWBERRIES, ROSES]
    combined_product = GIFT_BASKET

    orders = arbitrage(state, combined_product, component_products)

    orders_to_make.update(orders)