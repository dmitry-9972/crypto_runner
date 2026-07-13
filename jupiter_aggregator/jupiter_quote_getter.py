import requests
from tqdm import tqdm
from settings import secret_settings, consts

USDT_MINT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
# USDT_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC to check if it is more profitable (its not)

def to_atomic(amount: float, decimals: int) -> int:
    return int(amount * 10**decimals)

def from_atomic(amount: int, decimals: int) -> float:
    return amount / 10**decimals


def get_jupiter_quoute(input_mint, output_mint, input_amount):
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": input_amount,
        "slippageBps": 50,
    }

    headers = {
        "x-api-key": secret_settings.JUPITER_API_KEY
    }

    r = requests.get(
        "https://api.jup.ag/swap/v2/quote",
        params=params,
        headers=headers,
    )

    if not r.ok:
        print(r.json())
        raise Exception(r.json())

    r.raise_for_status()
    quote = r.json()

    in_amount = int(quote["inAmount"])
    out_amount = int(quote["outAmount"])

    return in_amount, out_amount



#
# in_amount, out_amount, price = get_jupiter_quoute(BONK_MINT, USDT_MINT, amount_bonk)
# print(f"Продажа: {in_amount} BONK")
# print(f"Получим: {out_amount} USDT")
# print(f"Цена: {price:.10f} USDT за BONK")

def get_prices_for_gate_from_jupiter(usdt_amount=10):
    reverse_dict = {}

    # for key, value in consts.GATE_SOL_CONTRACTS.items():
    #     reverse_dict[value['contract_address']] = key

    result = {}
    import time
    time_delay = 1
    import sys
    for key in tqdm(consts.GATE_SOL_CONTRACTS.keys(), colour='green', file=sys.stdout):
        try:
            mint_to_get_quote = consts.GATE_SOL_CONTRACTS[key]['contract_address']

            if USDT_MINT == mint_to_get_quote:
                continue  # {'error': 'inputMint cannot be same as outputMint'}

            usdt_decimals = consts.GATE_SOL_CONTRACTS['USDT']['decimals']
            usdt_in_amount = to_atomic(usdt_amount, usdt_decimals)

            in_amount, out_amount = get_jupiter_quoute(USDT_MINT, mint_to_get_quote, usdt_in_amount)
            out_decimals = consts.GATE_SOL_CONTRACTS[key]['decimals']
            out_real_amount = from_atomic(out_amount, out_decimals)
            buy_price = 1 / (out_real_amount / usdt_amount)

            result[key+'/USDT'] = {'buy_price': buy_price}
            # print('****')
            # print('mint', key, mint_to_get_quote)
            # print(f"Продажа: {usdt_amount} USDT")
            # print(f"Получим: {out_real_amount} {key}")
            # print(f"Цена: {buy_price:.10f} {key} за USDT ")
            time.sleep(time_delay)

            mint_decimals = consts.GATE_SOL_CONTRACTS[key]['decimals']
            mint_in_real_amount = usdt_amount / buy_price
            mint_atomic_amount = to_atomic(mint_in_real_amount, mint_decimals)

            in_amount, out_amount = get_jupiter_quoute(mint_to_get_quote, USDT_MINT, mint_atomic_amount)
            out_real_amount = from_atomic(out_amount, usdt_decimals)
            sell_price = out_real_amount / mint_in_real_amount

            result[key+'/USDT']['sell_price'] = sell_price
            # print('****')
            # print('mint', key, mint_to_get_quote)
            # print(f"Продажа: {mint_in_real_amount} {key}")
            # print(f"Получим: {out_real_amount} USDT")
            # print(f"Цена: {sell_price:.10f}  USDT за {key} ")
            time.sleep(time_delay)
        except Exception as e:
            print(e)
            time.sleep(time_delay)

    return result

# res =get_prices_for_gate_from_jupiter()
# print(res)