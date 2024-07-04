from datamodel import Order


class Orders():
    def __init__(self):
        self._orders = {}

    def get_orders(self):
        return self._orders

    # def __getitem__(self, symbol):
    #     return self._orders.setdefault(symbol, [])

    def place_order(self, symbol, price, quantity):
        BUY_SELL = None
        if quantity> 0:
            BUY_SELL = "BUY"
        elif quantity< 0:
            BUY_SELL = "SELL"

        print(f"{BUY_SELL} {quantity} at {price}")
        self._orders.setdefault(symbol, []).append(Order(symbol, price, quantity))