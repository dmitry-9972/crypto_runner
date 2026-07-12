from site_formatters import remove_slash_and_add_m_formatter, slash_to_underscore_formatter, dash_formatter, \
    remove_slash_formatter, idle_formatter, remove_slash_and_add_dash_formatter


LIMITATION_BY_GROUP = 100
SOUND_ON = False

# alerts window
SPREAD_FILTER = 1.03
FUNDING_FILTER = 1.02
SPOT_TO_FUTURES_SPREAD_FILTER = 1.01
SPOT_TO_FUTURES_FUNDING_FILTER = 1.02
SPOT_TO_SPOT_SPREAD_FILTER = 1.0000001
MARK_PRICE_SPREAD_FILTER = 1.02

SPOT_ARBITRAGE_PROFIT_MIN_PERCENT = 1


IGNORE_CACHE_EXPIRE_HOURS = 2

DO_CLEAR_ALL_CACHES = False
FILTER_BY_ONLY_TICKER = None
# FILTER_BY_ONLY_TICKER = 'INIT'



EXCHANGES = [
      'mexc',
    # # #    'bingx',
    'bybit',
    # 'aster',
     'kucoin',
     'gate',
    # 'bitget',
    #  'lbank',
    # #                  # kraken?
    # # #                   # 'okx',
    # # #                    # 'htx',
    #  ХТ и COINEX orbit?
    #

    # 'binance',   не регистрирует россиян
]

EXCHANGES_SITES = {
    'mexc': "https://www.mexc.com/futures/",              # https://www.mexc.com/futures/STG_USDT
    'bybit': "https://www.bybit.com/trade/usdt/",         # https://www.bybit.com/trade/usdt/BPUSDT
    'binance': "https://www.binance.com/en/futures/",     # https://www.binance.com/en/futures/HOMEUSDT
    # 'htx':None,
    'kucoin': "https://www.kucoin.com/ru/trade/futures/", # https://www.kucoin.com/ru/trade/futures/BPUSDTM
    'okx': None,
    'bingx': "https://bingx.com/en/perpetual/",           # https://bingx.com/en/perpetual/HOME-USDT
    'gate': "https://www.gate.com/futures/USDT/",         # https://www.gate.com/futures/USDT/BTC_USDT
    'bitget': "https://www.bitget.com/ru/futures/usdt/",  # https://www.bitget.com/ru/futures/usdt/BTCUSDT
    'lbank': "https://www.lbank.com/futures/",            # https://www.lbank.com/futures/truthusdt
}

SPOT_EXCHANGES_SITES = {
    'mexc': "https://www.mexc.com/exchange/",   # https://www.mexc.com/exchange/DEUS_USDT
    'bybit': "https://www.bybit.com/trade/spot/",              # https://www.bybit.com/en/trade/spot/TRUMP/USDC
    'binance': "https://www.binance.com/en/futures/",
    # 'htx':None,
    'kucoin': "https://www.kucoin.com/ru/trade/",  # https://www.kucoin.com/ru/trade/DEUS-USDT
    'okx': None,
    'bingx': "https://bingx.com/en/perpetual/",
    'gate': "https://www.gate.com/trade/",
    'bitget': "https://www.bitget.com/ru/futures/usdt/",
    'lbank': "https://www.lbank.com/futures/",
}



EXCHANGES_SITES_FORMATTERS = {
    'mexc': slash_to_underscore_formatter,                                  # https://www.mexc.com/futures/STG_USDT
    'bybit': remove_slash_formatter,                                        # https://www.bybit.com/trade/usdt/BPUSDT
    'binance': remove_slash_formatter,                                      # https://www.binance.com/en/futures/HOMEUSDT
    # 'htx':None,
    'kucoin': remove_slash_and_add_m_formatter,                             # https://www.kucoin.com/ru/trade/futures/BPUSDTM
    # 'okx':None,
    'bingx': dash_formatter,                                               # https://bingx.com/en/perpetual/HOME-USDT
    'gate': slash_to_underscore_formatter,                                  # https://www.gate.com/futures/USDT/BTC_USDT
    'bitget': remove_slash_formatter,                                       # https://www.bitget.com/ru/futures/usdt/BTCUSDT
    'lbank': remove_slash_formatter,
}


SPOT_EXCHANGES_SITES_FORMATTERS = {
    'mexc': slash_to_underscore_formatter,   # https://www.mexc.com/exchange/DEUS_USDT
    'bybit': idle_formatter,                                        # https://www.bybit.com/trade/usdt/BPUSDT
    'binance': remove_slash_formatter,
    # 'htx':None,
    'kucoin': remove_slash_and_add_dash_formatter,
    # 'okx':None,
    'bingx': dash_formatter,
    'gate': slash_to_underscore_formatter,                                  # https://www.gate.com/futures/USDT/BTC_USDT
    'bitget': remove_slash_formatter,
    'lbank': remove_slash_formatter,
}


SPLITTED_IN_TWO = ['TQQQX/USDT']


SPOT_DEPOSIT_LINKS = {
    'mexc': 'https://www.mexc.com/assets/deposit/',
    'bybit': 'https://www.bybit.com/en/user/assets/deposit/',
    'kucoin': 'https://www.kucoin.com/ru/assets/coin/',
    'gate': 'https://www.gate.com/myaccount/funds/deposit/',
}

SPOT_WITHDRAW_LINKS = {
    'mexc': 'https://www.mexc.com/assets/withdraw/',
    'bybit': 'https://www.bybit.com/en/user/assets/withdraw/',
    'kucoin': 'https://www.kucoin.com/ru/assets/withdraw/',
    'gate': 'https://www.gate.com/myaccount/funds/withdraw/' ,
}
