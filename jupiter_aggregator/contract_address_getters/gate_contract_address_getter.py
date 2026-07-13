# import requests
#
# url = "https://api.gateio.ws/api/v4/wallet/currency_chains"
# params = {
#     "currency": "BONK"
# }
#
# r = requests.get(url, params=params)
# print(r.json())
import asyncio

import requests
import time

from jupiter_aggregator.decimals_parser import get_decimals_for_mint

url = "https://api.gateio.ws/api/v4/spot/currencies"

r = requests.get(url, )

gate_sol_token_adresses = {}
for d in r.json():
    if d['delisted']:
        continue

    for chain in d['chains']:
        if chain['name'] == 'SOL':

            if 'invalid' in chain['addr'] or not chain['addr']:
                continue
            print(chain['addr'])
            decimals = asyncio.run(get_decimals_for_mint(chain['addr']))

            time.sleep(1)

            print(d['currency'],
                  chain['name'],
                  chain['addr'],
                  'withdraw_disabled',
                  d['withdraw_disabled'],
                  'deposit_disabled',
                  d['deposit_disabled'],
                  'decimals', decimals)

            gate_sol_token_adresses[d['currency']] = {
                "currency": d['currency'],
                "chain_name": chain['name'],
                "contract_address": chain['addr'],
                'withdraw_disabled': d['withdraw_disabled'],
                'deposit_disabled': d['deposit_disabled'],
                'decimals': decimals,
            }

from pprint import pprint
pprint(gate_sol_token_adresses)


