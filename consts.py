LIMITATION_BY_GROUP = 100
SOUND_ON = False

# alerts window
SPREAD_FILTER = 1.02
FUNDING_FILTER = 10.5
SPOT_TO_FUTURES_SPREAD_FILTER = 10.033
SPOT_TO_FUTURES_FUNDING_FILTER = 10.5
SPOT_TO_SPOT_SPREAD_FILTER = 1.01

IGNORE_CACHE_EXPIRE_HOURS = 2

DO_CLEAR_ALL_CACHES = False
FILTER_BY_ONLY_TICKER = None
# FILTER_BY_ONLY_TICKER = 'INIT'



EXCHANGES = [
  # 'mexc',
  #    'bingx',
      'bybit',
     # 'aster',
       'kucoin',
     'gate',
    # 'bitget',
    # 'lbank',
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
    'mexc': "https://www.mexc.com/futures/",
    'bybit': "https://www.bybit.com/trade/spot/",              # https://www.bybit.com/en/trade/spot/TRUMP/USDC
    'binance': "https://www.binance.com/en/futures/",
    # 'htx':None,
    'kucoin': "https://www.kucoin.com/ru/trade/futures/",
    'okx': None,
    'bingx': "https://bingx.com/en/perpetual/",
    'gate': "https://www.gate.com/trade/",
    'bitget': "https://www.bitget.com/ru/futures/usdt/",
    'lbank': "https://www.lbank.com/futures/",
}

from site_formatters import remove_slash_and_add_m_formatter, slash_to_underscore_formatter, dash_formatter, \
    remove_slash_formatter, idle_formatter

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
    'mexc': slash_to_underscore_formatter,
    'bybit': idle_formatter,                                        # https://www.bybit.com/trade/usdt/BPUSDT
    'binance': remove_slash_formatter,
    # 'htx':None,
    'kucoin': remove_slash_and_add_m_formatter,
    # 'okx':None,
    'bingx': dash_formatter,
    'gate': slash_to_underscore_formatter,                                  # https://www.gate.com/futures/USDT/BTC_USDT
    'bitget': remove_slash_formatter,
    'lbank': remove_slash_formatter,
}



BAN_STRS = [
    'mexc        to     gate       - HK50/USDT:USDT',
    'bybit       to     gate       - EDGE/USDT:USDT',
    'mexc        to     gate       - HK50/USDT:USDT',
    'kucoin      to     gate       - EDGE/USDT:USDT',
    'bybit       to     gate       - EDGE/USDT:USDT',
    'mexc        to     gate       - HK50/USDT:USDT',
    'kucoin      to     gate       - EDGE/USDT:USDT',
    'mexc        to     gate       - EDGE/USDT:USDT',
    'mexc        to     gate       - HK50/USDT:USDT',
    'binance     to     gate       - EDGE/USDT:USDT',
    'mexc        to     gate       - HK50/USDT:USDT',
    'mexc        to     gate       - HK50/USDT:USDT',
    'gate        to     bitget     - EDGE/USDT:USDT',
    'gate        to     lbank      - ASTEROID/USDT:USDT',
    'bybit       to     lbank      - 1000XEC/USDT:USDT',
    'mexc        to     lbank      - ASTEROID/USDT:USDT',
    'lbank      - HK50/USDT:USDT',
    'lbank      - 1000XEC/USDT:USDT',
    'bitget     - CAT/USDT:USDT',
    'bitget     - ADI/USDT:USDT',
    'bitget      to     lbank      - CAT/USDT',
    'mexc        to     gate       - ALL',
    'gate       - BP',
    'gate       - MBOX',
    'bybit      - MBOX',
    'BEAM',
    'EDGE',
    'MBOX',
    'GUA',
    'SIREN',
    'TQQQX',
    'ESPORTS',
    'VANRY',
    'RAVE',


]



SPLITTED_IN_TWO = ['TQQQX/USDT']

