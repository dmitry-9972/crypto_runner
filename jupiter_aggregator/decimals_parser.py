def to_atomic(amount: float, decimals: int) -> int:
    return int(amount * 10**decimals)

def from_atomic(amount: int, decimals: int) -> float:
    return amount / 10**decimals

# from solders.pubkey import Pubkey
# from spl.token.client import Token
# from solana.rpc.api import Client
#
# client = Client("https://api.mainnet-beta.solana.com")
#
# mint = Pubkey.from_string("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263")
#
# info = client.get_account_info(mint)
#
# # Затем распарсить Mint Account и получить decimals.

#
# import asyncio
# from solders.pubkey import Pubkey
# from solana.rpc.async_api import AsyncClient
#
#
# async def main():
#     # Инициализируем асинхронный клиент
#     async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
#         # Адрес токена BONK
#         mint = Pubkey.from_string("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263")
#
#         # Получаем данные аккаунта
#         response = client.get_account_info(mint)
#         account_info = await response
#
#         if account_info.value:
#             print("Данные успешно получены!")
#             print(f"Владелец программы (Owner): {account_info.value.owner}")
#             # Сырые данные аккаунта (будут содержать decimals)
#             print(f"Размер данных (Data length): {len(account_info.value.data)} bytes")
#         else:
#             print("Аккаунт не найден.")
#
#
# # Запуск асинхронного скрипта
# asyncio.run(main())


import asyncio
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

# Импортируем лейаут для десериализации данных минта токена
from spl.token._layouts import MINT_LAYOUT

mint = 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263'

async def get_decimals_for_mint(mint):
    # Инициализируем асинхронный клиент
    async with AsyncClient("https://api.mainnet-beta.solana.com") as client:
        # Адрес токена BONK (можно заменить на любой другой SPL-токен)
        mint_address = Pubkey.from_string(mint)

        # Получаем данные аккаунта токена
        response = await client.get_account_info(mint_address)

        if response.value and response.value.data:
            # Декодируем сырые байты с помощью структуры MINT_LAYOUT
            parsed_data = MINT_LAYOUT.parse(response.value.data)

            # Извлекаем поле decimals
            token_decimals = parsed_data.decimals

            # print(f"Токен: {mint_address}")
            # print(f"Количество знаков после запятой (decimals): {token_decimals}")

            # Бонус: можно узнать общую эмиссию (в сырых единицах) и другие данные
            # print(f"Общая эмиссия (raw supply): {parsed_data.supply}")
            return token_decimals
        else:
            print("Не удалось найти аккаунт токена или данные пусты.")


# from settings.gate_sol_contracts import GATE_SOL_CONTRACTS
# # Запуск асинхронного скрипта
# import time
# for k, v in GATE_SOL_CONTRACTS.items():
#
#     mint = v['contract_address']
#     decimals = asyncio.run(get_decimals_for_mint(mint))
#     print(k, decimals, v['contract_address'])
#     time.sleep(1)




