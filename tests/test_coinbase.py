from coinbase.rest import RESTClient
from json import dumps
import math

import dotenv

cdp_api_key_name = dotenv.get_key("../app/.env", "CDP_API_KEY_NAME")
cdp_api_key_pk = dotenv.get_key("../app/.env", "CDP_API_KEY_PRIVATE_KEY")
if not cdp_api_key_name or not cdp_api_key_pk:
    raise ValueError("CDP keys are not set")

client = RESTClient(api_key=cdp_api_key_name, api_secret=cdp_api_key_pk)

product = client.get_product("BTC-USD")
btc_usd_price = float(product["price"])
adjusted_btc_usd_price = str(math.floor(btc_usd_price - (btc_usd_price * 0.05)))

print("BTC-USD Price: ", btc_usd_price)