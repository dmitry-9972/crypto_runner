import requests

from settings import secret_settings, consts

USDT_MINT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"

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
        exit()

    r.raise_for_status()
    quote = r.json()

    in_amount = int(quote["inAmount"])
    out_amount = int(quote["outAmount"])



    if input_mint == USDT_MINT:
        price = in_amount / out_amount
    else:
        price = out_amount / in_amount

    return in_amount, out_amount, price



#
# in_amount, out_amount, price = get_jupiter_quoute(BONK_MINT, USDT_MINT, amount_bonk)
# print(f"Продажа: {in_amount} BONK")
# print(f"Получим: {out_amount} USDT")
# print(f"Цена: {price:.10f} USDT за BONK")

def get_prices_for_gate_from_jupiter():
    reverse_dict = {}

    # for key, value in consts.GATE_SOL_CONTRACTS.items():
    #     reverse_dict[value['contract_address']] = key

    result = {}
    import time
    time.sleep(1)
    for key in consts.GATE_SOL_CONTRACTS.keys():
        mint_to_get_quote = consts.GATE_SOL_CONTRACTS[key]['contract_address']

        in_amount, out_amount, buy_price = get_jupiter_quoute(USDT_MINT, mint_to_get_quote, 10000000)
        result[key] = {'buy_price': buy_price}
        print('****')
        print('mint', key, mint_to_get_quote)
        print(f"Продажа: {in_amount} USDT")
        print(f"Получим: {out_amount} {key}")
        print(f"Цена: {buy_price:.10f} {key} за USDT ")
        exit()

        # in_amount, out_amount, sell_price = get_jupiter_quoute(mint_to_get_quote, USDT_MINT, out_amount)
        # result[key] = {'sell_price': sell_price}

get_prices_for_gate_from_jupiter()