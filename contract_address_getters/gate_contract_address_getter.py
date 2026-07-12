# import requests
#
# url = "https://api.gateio.ws/api/v4/wallet/currency_chains"
# params = {
#     "currency": "BONK"
# }
#
# r = requests.get(url, params=params)
# print(r.json())

import requests

url = "https://api.gateio.ws/api/v4/spot/currencies"

r = requests.get(url, )

gate_sol_token_adresses = {}
for d in r.json():
    if d['delisted']:
        continue

    for chain in d['chains']:
        if chain['name'] == 'SOL':
            print(d['currency'],
                  chain['name'],
                  chain['addr'],
                  'withdraw_disabled',
                  d['withdraw_disabled'],
                  'deposit_disabled',
                  d['deposit_disabled'])

            gate_sol_token_adresses[d['currency']] = {
                "currency": d['currency'],
                "chain_name": chain['name'],
                "contract_address": chain['addr'],
                'withdraw_disabled': d['withdraw_disabled'],
                'deposit_disabled': d['deposit_disabled']
            }

from pprint import pprint
pprint(gate_sol_token_adresses)


