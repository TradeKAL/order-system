from abc import ABCMeta, abstractmethod


class TradeAPIInterface(metaclass=ABCMeta):
    @abstractmethod
    def market_buy(self, order_currency, pay_currency, units):
        pass

    @abstractmethod
    def market_sell(self, order_currency, pay_currency, units):
        pass

    @abstractmethod
    def limit_buy(self, order_currency, pay_currency, units, price):
        pass

    @abstractmethod
    def limit_sell(self, order_currency, pay_currency, units, price):
        pass
