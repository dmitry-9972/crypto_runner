from decimal import Decimal

import consts


def get_exchange_client_by_exchange_name(comparer, exchange_name1):
    exchange_client_by_exchange_name = [exchange_client for
                                     exchange_client in comparer.all_exchanges
                                     if exchange_client.exchange_name == exchange_name1]
    exchange_client = exchange_client_by_exchange_name[0] if exchange_client_by_exchange_name else None
    return exchange_client

def update_symbol_for_specific_exchange_if_needed(exchange_name=None, symbol=None, s_to_f=None):
    symbol_updated = symbol

    if s_to_f:
        return symbol

    if exchange_name in ['lbank',]:
        # print("symbol")
        # print(symbol)
        # symbol_updated = symbol.replace(':','').replace('/','')
        # print(symbol_updated)
        # return symbol_updated
        return symbol
    # if exchange_name in ['bybit', 'gate', 'mexc', 'binance', 'bingx']:
    #     symbol_updated = symbol + ":USDT"
    symbol_updated = symbol + ":USDT"


    return symbol_updated


def get_funding_gain(p1: float, p2: float, fr1: float, fr2: float) -> float:
    """
    Рассчитывает суммарный funding gain/loss для арбитражной позиции:
    - Long на бирже с меньшей ценой
    - Short на бирже с большей ценой

    Параметры:
        p1, p2: цены на двух биржах
        fr1, fr2: funding rates (в decimal, например 0.0001 = 0.01%)

    Возвращает:
        Суммарный funding за один период (положительное = прибыль)
    """
    if 'N\A' in [fr1, fr2]:
        return 'N\A'

    if p1 == p2:
        return 0.0  # нет арбитража

    # Определяем, где long, где short
    if p1 > p2:
        # Short на 1 (дорого), Long на 2 (дешево)
        # Short получает funding если fr > 0, платит если fr < 0
        funding_short = fr1  # для short: +fr (получаем, если положительный)
        funding_long = -fr2  # для long: -fr (платим, если положительный)
    else:
        # Short на 2, Long на 1
        funding_short = fr2
        funding_long = -fr1

    # Суммарный funding (на одну единицу позиции)
    net_funding = funding_short + funding_long

    return net_funding


def get_spread(a , b):
    return round(max(a, b) / min(a, b), 7)

def get_future_to_spot_spread(a , b):
    return round(b / a, 7)


def check_for_ban_strs(line):
    import consts
    for ban_key in consts.BAN_STRS:
        if ban_key in line:
            return True


def get_prepared_dict_for_all_exchanges(comparer, symbol, exchanges_list ):
    prepared_dict = {}

    exchanges_list = comparer.all_exchanges

    for exchange in exchanges_list:
        if not comparer.all_possible_prices[exchange.exchange_name].get(symbol):
            continue

        prepared_dict[exchange.exchange_name] = {
            'current_price': Decimal(comparer.all_possible_prices[exchange.exchange_name].get(symbol))}

    sum = 0
    items_num = len(prepared_dict.keys())
    for k, v in prepared_dict.items():
        sum += v['current_price']
    average = sum / items_num if items_num else 0

    for k, v in prepared_dict.items():
        prepared_dict[k]['delta'] = abs(v["current_price"] - average)

    # prepared_dict = dict(sorted(prepared_dict.items(), key=lambda item: item[1]['delta'], reverse=True))

    for k, v in prepared_dict.items():
        prepared_dict[k]['current_price'] = f'{v["current_price"]:.6f}'
        prepared_dict[k]['average'] = f'{Decimal(average):.6f}'
        prepared_dict[k]['delta'] = f'{v["delta"]:.6f}'

    return prepared_dict


def get_spread_alerts_and_funding_alerts(line_dict, ignored_cache):
    line_dict = {
        k: v for k, v in line_dict.items() if not ignored_cache.check(v)
    }


    spread_alerts = {
        k: v
        for k, v in sorted(
            (item for item in line_dict.items() if item[1].get('spread', 0) > consts.SPREAD_FILTER and
             not item[1].get('spot_futures_comparison')),
            key=lambda item: item[1].get('spread', 0),
            reverse=True
        )
    }

    funding_alerts = {
        k: v
        for k, v in sorted(
            (item for item in line_dict.items() if item[1].get('funding_gain', 0) > consts.FUNDING_FILTER and
             not item[1].get('spot_futures_comparison')),
            key=lambda item: item[1].get('funding_gain', 0),
            reverse=True
        )
    }

    spot_to_futures_spread_alerts = {
        k: v
        for k, v in sorted(
            (item for item in line_dict.items() if item[1].get('spread', 0) > consts.SPOT_TO_FUTURES_SPREAD_FILTER and
             item[1].get('spot_futures_comparison')),
            key=lambda item: item[1].get('spread', 0),
            reverse=True
        )
    }

    spot_to_futures_funding_alerts = {
        k: v
        for k, v in sorted(
            (item for item in line_dict.items() if item[1].get('funding_gain', 0) > consts.SPOT_TO_FUTURES_FUNDING_FILTER and
             item[1].get('spot_futures_comparison')),
            key=lambda item: item[1].get('funding_gain', 0),
            reverse=True
        )
    }

    return spread_alerts, funding_alerts, spot_to_futures_spread_alerts, spot_to_futures_funding_alerts


def get_funding_rate_interval(raw):
    interval = raw.get('interval') or \
               raw.get('fundingInterval') or \
               raw.get('interval') or \
               raw.get('funding_interval') or \
               raw.get('collectCycle')
    return interval

