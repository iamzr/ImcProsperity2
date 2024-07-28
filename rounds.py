from abc import ABC, abstractmethod
from datamodel import TradingState
from orders import Orders
from products import AMETHYSTS, CHOCOLATE, COCONUT, COCONUT_COUPON, GIFT_BASKET, ROSES, STARFRUIT, STRAWBERRIES
from strategies import AcceptablePriceStrategy, AcceptablePriceWithEmaStrategy, SpreadTradingStrategy, VanillaOptionsPricing, ema, get_mid_price 

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

        s = AcceptablePriceStrategy(state=self._state, orders=self._orders, product=AMETHYSTS, acceptable_ask_price=acceptable_ask_price_amethysts, acceptable_bid_price=acceptable_bid_price_amethysts)
        s.run()

        # star fruit

        starfruit_span = 6

        s = AcceptablePriceWithEmaStrategy(state=self._state, orders=self._orders, trader_data=self._trader_data, product=STARFRUIT, span=starfruit_span)
        s.run()

def get_gift_basket_price(chocolate, roses, strawberries):
    return 4 * chocolate + roses + 6 * strawberries

class Round3(Round):
    def _run(self):
        component_products = [CHOCOLATE, STRAWBERRIES, ROSES]
        combined_product = [GIFT_BASKET]

        gift_basket_price = get_mid_price(self._state, GIFT_BASKET)

        if gift_basket_price is None:
            return

        components_price = get_gift_basket_price(get_mid_price(self._state, CHOCOLATE), get_mid_price(self._state, ROSES), get_mid_price(self._state, STRAWBERRIES))

        SPREAD_MEAN = 376.0862
        SPREAD_STD = 76.354

        s = SpreadTradingStrategy(state=self._state, 
                                  orders=self._orders, 
                                  portfolio_1=combined_product, 
                                  portfolio_1_price=int(gift_basket_price),
                                  portfolio_2=component_products,
                                  portfolio_2_price=int(components_price),
                                  spread_mean=SPREAD_MEAN,
                                  spread_std=SPREAD_STD,
                                  threshold=1
                                  )
        s.run()

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
        vol = 0.19 # volativity of the coconuts

        price_of_coupons = VanillaOptionsPricing().call_price(coconuts_midprice, strike_price, risk_free_rate, vol, time_to_maturity)
        # price_of_coupons = 600

        print("here", coupons_midprice, price_of_coupons)

        s = AcceptablePriceStrategy(state=self._state, orders=self._orders, product=COCONUT_COUPON, acceptable_ask_price=price_of_coupons, acceptable_bid_price=price_of_coupons)
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