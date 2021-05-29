import hashlib
import os
import uuid
from enum import Enum
from urllib.parse import urlencode

import jwt
import requests

from api.interface import TradeAPIInterface


class UpbitAPI:
    BASE_URL = "https://api.upbit.com"

    def __init__(self):
        self.session = requests.session()

        # TODO: vault 도입 검토
        self.access_key = os.environ["UPBIT_OPEN_API_ACCESS_KEY"]
        self.secret_key = os.environ["UPBIT_OPEN_API_SECRET_KEY"]

    def _get_payload(self, query):
        payload = {
            "access_key": self.access_key,
            "nonce": str(uuid.uuid4()),
        }

        if query:
            query_string = urlencode(query).encode()
            m = hashlib.sha512()
            m.update(query_string)

            payload["query_hash"] = m.hexdigest()
            payload["query_hash_alg"] = "SHA512"

        return payload

    def get_headers(self, query=None):
        payload = self._get_payload(query)
        jwt_token = jwt.encode(payload, self.secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        return {"Authorization": authorize_token}


class UpbitTradeAPI(UpbitAPI, TradeAPIInterface):
    class Side(str, Enum):
        BID = "bid"  # 매수
        ASK = "ask"  # 매도

    class OrderType(str, Enum):
        LIMIT = "limit"     # 지정가 주문
        PRICE = "price"     # 시장가 주문(매수)
        MARKET = "market"   # 시장가 주문(매도)

    def __init__(self):
        super().__init__()

        self.urls = {
            "order": f"{self.BASE_URL}/v1/orders",
            "cancel_order": f"{self.BASE_URL}/v1/order",
        }

    def _order(self, query):
        headers = self.get_headers(query)
        return self.session.post(self.urls["order"], params=query, headers=headers, timeout=3)

    def market_sell(self, order_currency, pay_currency, units):
        query = {
            "market": f"{order_currency}-{pay_currency}",
            "side": self.Side.ASK,
            "volume": units,
            "ord_type": self.OrderType.MARKET,
        }
        return self._order(query)

    def market_buy(self, order_currency, pay_currency, units):
        # TODO: price 계산
        query = {
            "market": f"{pay_currency}-{order_currency}",
            "side": self.Side.BID,
            "price": "100.0",
            "ord_type": self.OrderType.PRICE,
        }
        return self._order(query)

    def limit_sell(self, order_currency, pay_currency, units, price):
        query = {
            "market": f"{order_currency}-{pay_currency}",
            "side": self.Side.ASK,
            "volume": units,
            "price": price,
            "ord_type": self.OrderType.MARKET,
        }
        return self._order(query)

    def limit_buy(self, order_currency, pay_currency, units, price):
        query = {
            "market": f"{order_currency}-{pay_currency}",
            "side": self.Side.BID,
            "volume": units,
            "price": price,
            "ord_type": self.OrderType.MARKET,
        }
        return self._order(query)
