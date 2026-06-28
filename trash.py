# from client import ExchangeClient
#
# print('testing with', 'lbank')
# exchange_client = ExchangeClient('lbank')
#
# # exchange_client.get_all_symbols()
# # while 1:
# #     exchange_client.get_prices(symbol='BTC/USDT')
# #     time.sleep(5)
#
# exchange_client.get_all_futures_symbols()
#
# # for k, v in exchange_client.futures_symbols_dict.items():
# #     print(k, v)
# 'ANTHROPIC/USDT:USDT'
# exchange_client.get_prices(list(exchange_client.futures_symbols_dict.keys()))
# print(exchange_client.current_prices)
#

# from playsound import playsound
#
# playsound("sounds/Alarm01.wav", block=False)
#
# print('123')

# import winsound
#
# winsound.PlaySound("sounds/Alarm01.wav",
#                   winsound.SND_FILENAME | winsound.SND_ASYNC)
#
# print('123')

import ctypes
ctypes.windll.winmm.mciSendStringW("play sounds/Alarm01.wav wait", None, 0, None)