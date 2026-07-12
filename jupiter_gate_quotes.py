import time
from pprint import pprint

import requests

import consts
import secret_settings
from utils import chunk_iterator

######################################################### SOLO TOKEN

# response = requests.get(
#     'https://api.jup.ag/price/v3',
#     params={'ids': 'So11111111111111111111111111111111111111112'},
#     headers={'x-api-key': secret_settings.JUPITER_API_KEY}
# )
# response.raise_for_status()
# prices = response.json()
# sol_price = prices['So11111111111111111111111111111111111111112']['usdPrice']
# print(f"SOL: ${sol_price}")


######################################################### MULTIPLR TOKEN

import requests

# mints = [
#     'So11111111111111111111111111111111111111112',  # SOL
#     'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN', # JUP
#     'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', # USDC,
#     'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263', # BONK
#
# ]

# response = requests.get(
#     'https://api.jup.ag/price/v3',
#     params={'ids': ','.join(mints)},
#     headers={'x-api-key': secret_settings.JUPITER_API_KEY}
# )
# prices = response.json()
#
# for mint, data in prices.items():
#     print(f"{mint}: ${data['usdPrice']}")

def get_prices_for_gate_from_jupiter():
    reverse_dict = {}

    for key, value in consts.GATE_SOL_CONTRACTS.items():
        reverse_dict[value['contract_address']] = key

    result = {}
    for chunk in chunk_iterator(list(consts.GATE_SOL_CONTRACTS.keys()), 40):
        time.sleep(1)
        mints = []

        for key in chunk:
            mints.append(consts.GATE_SOL_CONTRACTS[key]['contract_address'])


        response = requests.get(
            'https://api.jup.ag/price/v3',
            params={'ids': ','.join(mints)},
            headers={'x-api-key': secret_settings.JUPITER_API_KEY}
        )
        prices = response.json()

        for mint, data in prices.items():
            # print(f"{reverse_dict[mint]}  {mint}: ${data.get('usdPrice') or 0}")

            if type(data) == dict and data.get('usdPrice'):
                # на самом деле это цена в долларах а не в юсдт, но я решил не париться
                # может будет отклонение на 2 тысячных
                result[reverse_dict[mint]+'/USDT'] = data.get('usdPrice')
            else:
                pass
                # print('something wrong with', data)


    return result

# result = get_prices_for_gate_from_jupiter()
# pprint(result)

