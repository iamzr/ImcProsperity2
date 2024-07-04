from datamodel import TradingState
from orders import Orders
from products import AMETHYSTS, CHOCOLATE, GIFT_BASKET, ROSES, STARFRUIT, STRAWBERRIES
from strategies import acceptable_price_strategy, ema, round_3_arbitrage


def round_1(state: TradingState, traderData: dict, orders: Orders):
    # amethysts 
    if not state.order_depths.get(AMETHYSTS):
        return

    acceptable_bid_price_amethysts = 10_000
    acceptable_ask_price_amethysts = 10_000

    acceptable_price_strategy(state=state, orders=orders, product=AMETHYSTS, acceptable_ask_price=acceptable_ask_price_amethysts, acceptable_bid_price=acceptable_bid_price_amethysts)

    # star fruit
    if not state.order_depths.get(STARFRUIT):
        return

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


def round_3(state: TradingState, traderData: dict, orders: Orders):
    component_products = [CHOCOLATE, STRAWBERRIES, ROSES]
    combined_product = GIFT_BASKET

    if not state.order_depths.get(GIFT_BASKET):
        return

    round_3_arbitrage(state, orders, combined_product, component_products)