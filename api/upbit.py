import hashlib
import os
import uuid
from urllib.parse import urlencode

import jwt
import requests


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
