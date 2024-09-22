from abc import ABC, abstractmethod
from math import inf
from datamodel import OrderDepth, Symbol, TradingState
from orders import Orders
from products import AMETHYSTS, CHOCOLATE, COCONUT, COCONUT_COUPON, GIFT_BASKET, ROSES, STARFRUIT, STRAWBERRIES
from strategies import AcceptablePriceStrategy, AcceptablePriceWithEmaStrategy, SpreadTradingStrategy, VanillaOptionsPricing, ema, get_best_ask, get_best_bid, get_mid_price 

class Round(ABC):
    def __init__(self, state: TradingState, traderData: dict, orders: Orders):
        self._state = state
        self._trader_data = traderData
        self._orders = orders
    
    @abstractmethod
    def _run(self):
        raise NotImplementedError()
    
    def run(self):
        return self._run()

class Round1(Round):
    def _run(self):
        # amethysts 
        if not self._state.order_depths.get(AMETHYSTS):
            return

        acceptable_bid_price_amethysts = 10_000
        acceptable_ask_price_amethysts = 10_000

        s = AcceptablePriceStrategy(state=self._state,
                                    orders=self._orders,
                                    product=AMETHYSTS,
                                    acceptable_ask_price=acceptable_ask_price_amethysts,
                                    acceptable_bid_price=acceptable_bid_price_amethysts,
                                    best_only=False)
        s.run()

        # star fruit

        starfruit_span = 6

        s = AcceptablePriceWithEmaStrategy(state=self._state,
                                           orders=self._orders,
                                           trader_data=self._trader_data,
                                           product=STARFRUIT,
                                           span=starfruit_span,
                                           best_only=False)
        s.run()

def get_gift_basket_price(chocolate, roses, strawberries):
    return 4 * chocolate + roses + 6 * strawberries

class Round3(Round):
    def _run(self):
        actual_mid_price = get_mid_price(self._state, GIFT_BASKET) # type: ignore

        if actual_mid_price is None:
            return

        # Step 1: calculate orderdepth for synthetic made up of the best bid and asks of underlying
        ratios = {
            CHOCOLATE: 4,
            ROSES: 1,
            STRAWBERRIES: 6
            
        }

        implied_bid = 0
        implied_ask = 0
        implied_bid_vol = inf
        implied_ask_vol = -inf

        implied_price = 0
        for symbol, ratio in ratios.items():
            best_bid, best_bid_vol = get_best_bid(state=self._state, symbol=symbol)
            best_ask, best_ask_vol = get_best_ask(state=self._state, symbol=symbol) 

            if best_bid is None or best_ask is None or best_bid_vol is None or best_ask_vol is None:
                return 

            # # TODO: figure out how to handle when there's no bids or asks
            implied_bid += best_bid * ratio
            implied_ask += best_ask  * ratio

            implied_bid_vol = min(best_bid_vol // ratio, implied_bid_vol)
            implied_ask_vol = max(best_ask_vol // ratio, implied_ask_vol)

            # implied_price += get_mid_price(state=self._state, symbol=symbol) * ratio

        
        # synthetic_orderdepth.buy_orders[implied_bid] = implied_bid_vol
        # synthetic_orderdepth.sell_orders[implied_ask_vol] = implied_ask_vol

        if implied_ask_vol == inf or implied_bid_vol == inf:
            return 

        synthetic_ask = implied_ask
        synthetic_bid = implied_bid


        # Step 2: calcaulte spread between synthetic and actual
        synthetic_mid_price = (implied_ask + implied_bid) / 2 


        spread = actual_mid_price - synthetic_mid_price
        # step 3: calculate z score
        SPREAD_MEAN = 376.0862
        SPREAD_STD = 76.354

        z_score = (spread - SPREAD_MEAN) / SPREAD_STD
        # step 4  calculate what to buy and sell
        threshold =  2

        if z_score > threshold:
            # sell gift baskets at best bid
            best_bid, best_bid_amount = get_best_bid(self._state, GIFT_BASKET)

            amount = min(best_bid_amount, implied_bid)
            self._orders.place_order(GIFT_BASKET, best_bid, -amount)

            # # buy syntheics
            for symbol, ratio in ratios.items():
                # if symbol == ROSES:
                #     continue

                vol = amount * ratio

                best_ask , _ = get_best_ask(self._state, symbol=symbol)
                self._orders.place_order(symbol=symbol, price=best_ask, quantity=-vol)

        elif z_score < -threshold:
            # buy gift baskets at best ask
            best_ask, best_ask_amount = get_best_ask(self._state, GIFT_BASKET)

            amount = min(best_ask_amount, implied_ask)
            self._orders.place_order(GIFT_BASKET,best_ask, -best_ask_amount)

            # sell synthetics
            for symbol, ratio in ratios.items():
                if symbol == ROSES:
                    continue
                    
                vol = amount * ratio

                best_bid , _ = get_best_bid(self._state, symbol=symbol)
                self._orders.place_order(symbol=symbol, price=best_bid, quantity=-vol)
    



class Round4(Round):
    def _run(self):

        coconuts_midprice = get_mid_price(self._state, COCONUT) # price of coconuts

        if coconuts_midprice is None:
            return

        coupons_midprice = get_mid_price(self._state, COCONUT_COUPON) 

        if coupons_midprice is None:
            return

        # for coconut coupons
        strike_price = 10_000
        time_to_maturity = 250/365

        risk_free_rate = 0.0
        vol = 0.19 # volatility of the coconuts

        price_of_coupons = VanillaOptionsPricing().call_price(coconuts_midprice, strike_price, risk_free_rate, vol, time_to_maturity)
        # price_of_coupons = 600

        s = AcceptablePriceStrategy(state=self._state,
                                    orders=self._orders,
                                    product=COCONUT_COUPON,
                                    acceptable_ask_price=price_of_coupons,
                                    acceptable_bid_price=price_of_coupons,
                                    )
        s.run()

        # part 2
        SPREAD_MEAN = 9000.263400
        SPREAD_STD = 50.559215
        # SPREAD_MEAN = 9300 SPREAD_STD = 2k

        s = SpreadTradingStrategy(state=self._state, 
                                  orders=self._orders, 
                                  portfolio_1=[COCONUT], 
                                  portfolio_1_price=int(coconuts_midprice),
                                  portfolio_2=[COCONUT_COUPON],
                                  portfolio_2_price=int(coupons_midprice),
                                  spread_mean=SPREAD_MEAN,
                                  spread_std=SPREAD_STD,
                                  threshold=2
                                  )
        # s.run()