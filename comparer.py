import time

import consts
from client import ExchangeClient
from itertools import combinations
from decimal import Decimal

from utils import get_exchange_client_by_exchange_name, get_spread, get_funding_gain, \
    get_future_to_spot_spread


class Comparer:
    last_refresh_time = None
    exchanges_names = consts.EXCHANGES
    print('exchanges_names')
    print(exchanges_names)
    all_possible_prices = {}
    all_possible_funding_rates = {}
    all_possible_spot_prices = {}
    comparison_results = {}
    all_exchanges = []
    all_downloaded_ohlcvs = {}

    # def get_ochlv(self, exchange_name, symbol='BTC/USDT', timeframe='15m'):
    #     exchange_client_by_exchange_name = get_exchange_client_by_exchange_name(self, exchange_name)
    #
    #     exchange = exchange_client_by_exchange_name.exchange
    #     ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=500)
    #     self.all_downloaded_ohlcvs[exchange_name][symbol] = ohlcv
    #     return ohlcv

    def refresh_all_exchanges_and_prices(self):
        if self.last_refresh_time and time.time() - self.last_refresh_time < 10:
            print('REFRESH COOLDOWN')
            return
        else:
            self.last_refresh_time = time.time()


        self.all_possible_prices = {}
        self.all_possible_funding_rates = {}
        #print(self.all_possible_funding_rates)

        self.comparison_results = {}
        self.spot_to_futures_comparison_results = {}
        self.spot_to_spot_comparison_results = {}

        for exchange_client in self.all_exchanges:
            self.refresh_current_exchange(exchange_client)
            # print('refreshing with', exchange_client.exchange_name)
            # exchange_client.refresh_prices_and_fundings()
            # self.all_possible_prices[exchange_client.exchange_name] = exchange_client.current_prices
            # self.all_possible_funding_rates[exchange_client.exchange_name] = exchange_client.current_funding_rates

            # print('***********')
            # print(self.all_possible_funding_rates)

    def refresh_current_exchange(self, exchange_client):
        exchange_client.refresh_prices_and_fundings()
        self.all_possible_prices[exchange_client.exchange_name] = exchange_client.current_prices
        self.all_possible_funding_rates[exchange_client.exchange_name] = exchange_client.current_funding_rates
        self.all_possible_spot_prices[exchange_client.exchange_name] = exchange_client.spot_current_prices


    def __init__(self):
        for exchange_name in self.exchanges_names:
            print('working with', exchange_name)
            exchange_client = ExchangeClient(exchange_name)
            self.all_exchanges.append(exchange_client)

        # self.refresh_all_exchanges_and_prices()


    def compare_all_to_all(self, by_spread=True):
        self.comparison_results = {}
        pairs = list(combinations(self.exchanges_names, 2))
        for pair in pairs:
            self.compare_by_name(*pair)

        if by_spread:
            sorted_data = dict(sorted(self.comparison_results.items(), key=lambda item: item[1]['spread'], reverse=True))
        else:
            sorted_data = dict(sorted(self.comparison_results.items(), key=lambda item: item[1]['funding_gain'], reverse=True))

        key = lambda x: (x is not None, x)
        return sorted_data

    def compare_by_name(self, first_exchange_name, second_exchange_name):
        # print('Comparing :', first_exchange_name, second_exchange_name)
        list1 = self.all_possible_prices[first_exchange_name].keys()
        list2 = self.all_possible_prices[second_exchange_name].keys()

        intersection = list(set(list1).intersection(set(list2)))
        # print('len intersection')
        # print(len(intersection))

        for symbol in intersection:
            a = self.all_possible_prices[first_exchange_name][symbol]
            b = self.all_possible_prices[second_exchange_name][symbol]

            if a is None or b is None:
                print('WRONG SYMBOL, EXCHANGE DOESN"T HAVE SUCH:')
                print(a)
                print(b)
                print(symbol)
                print(first_exchange_name)
                print(second_exchange_name)
                continue

            a_funding = self.all_possible_funding_rates[first_exchange_name].get(symbol)

            if a_funding is None:
                a_funding = 'N\A'

            b_funding = self.all_possible_funding_rates[second_exchange_name].get(symbol) or 'N\A'

            if b_funding is None:
                b_funding = 'N\A'

            if 'N\A' in [a_funding, b_funding]:
                funding_gain = -99999
            else:
                funding_gain = get_funding_gain(float(a),
                                                float(b),
                                                float(a_funding),
                                                float(b_funding))
                funding_gain = Decimal(funding_gain) * 100

            # if 'IWM' in symbol and first_exchange_name in ['bybit', 'gate',]:
            #     print('IWM')
            #     print(a_funding)
            #     print(b_funding)
            #     print('funding_gain')
            #     print(funding_gain)

            # key_str = f"{first_exchange_name.strip():<10}  to     {second_exchange_name.strip():<10} - {symbol.strip():<20} ::: {a:<10} ::: {b:<10}"

            key_str = f"{first_exchange_name.strip():<10}  to     {second_exchange_name.strip():<10} - {symbol.strip():<20}"
            self.comparison_results[key_str] = {'spread': get_spread(a, b),
                                                'first_exchange_name': first_exchange_name.strip(),
                                                'second_exchange_name': second_exchange_name.strip(),
                                                'symbol': symbol.strip(),
                                                'price1': a,
                                                'price2': b,
                                                'funding_rate_1': a_funding,
                                                'funding_rate_2': b_funding,
                                                'funding_gain': funding_gain,
                                                }

    def compare_spot_to_futures_all_to_all(self, by_spread=True):
        self.spot_to_futures_comparison_results = {}
        pairs = list(combinations(self.exchanges_names, 2))
        for pair in pairs:
            ex1, ex2 = pair

            self.compare_spot_to_futures_by_name(ex1, ex1)
            self.compare_spot_to_futures_by_name(ex2, ex2)
            self.compare_spot_to_futures_by_name(ex1, ex2)
            self.compare_spot_to_futures_by_name(ex2, ex1)

        if by_spread:
            sorted_data = dict(sorted(self.spot_to_futures_comparison_results.items(), key=lambda item: item[1]['spread'], reverse=True))
        else:
            sorted_data = dict(sorted(self.spot_to_futures_comparison_results.items(), key=lambda item: item[1]['funding_gain'], reverse=True))

        return sorted_data


    def compare_spot_to_futures_by_name(self, spot_exchange_name, futures_exchange_name):
        list1 = self.all_possible_spot_prices[spot_exchange_name].keys()
        list2 = self.all_possible_prices[futures_exchange_name].keys()
        list2_removed_usdt = [x.replace(':USDT', '') for x in list2]

        intersection = list(set(list1).intersection(set(list2_removed_usdt)))

        for symbol in intersection:
            a = self.all_possible_spot_prices[spot_exchange_name][symbol]
            b = self.all_possible_prices[futures_exchange_name][symbol+':USDT']

            if a > b:   # spot should be chipper than future. We cant short spot.
                continue

            if a is None or b is None:
                print('WRONG SYMBOL, EXCHANGE DOESN"T HAVE SUCH:')
                print(a)
                print(b)
                print(symbol)
                print(spot_exchange_name)
                print(futures_exchange_name)
                continue

            a_funding = 0
            b_funding = self.all_possible_funding_rates[futures_exchange_name].get(symbol+':USDT') or 'N\A'

            if b_funding is None:
                b_funding = 'N\A'

            if 'N\A' in [a_funding, b_funding]:
                funding_gain = -99999
            else:
                funding_gain = get_funding_gain(float(a),
                                                float(b),
                                                float(a_funding),
                                                float(b_funding))
                funding_gain = Decimal(funding_gain) * 100

            key_str = f"{spot_exchange_name.strip():<10} S  to     {futures_exchange_name.strip():<10} F - {symbol.strip():<20}"
            self.spot_to_futures_comparison_results[key_str] = {'spread': get_future_to_spot_spread(a, b),
                                                                'first_exchange_name': spot_exchange_name.strip(),
                                                                'second_exchange_name': futures_exchange_name.strip(),
                                                                'symbol': symbol.strip(),
                                                                'price1': a,
                                                                'price2': b,
                                                                'funding_rate_1': a_funding,
                                                                'funding_rate_2': b_funding,
                                                                'funding_gain': funding_gain,
                                                                'spot_futures_comparison': True,
                                                                'spot_symbol': symbol.strip(),
                                                                'futures_symbol': symbol+':USDT',
                                                                'spot_exchange_name': spot_exchange_name.strip(),
                                                                'futures_exchange_name': futures_exchange_name.strip(),
                                                                }

    def compare_spot_to_spot_all_to_all(self, ):
        self.spot_to_futures_comparison_results = {}
        pairs = list(combinations(self.exchanges_names, 2))
        for pair in pairs:
            ex1, ex2 = pair
            self.compare_spot_to_spot_by_name(ex1, ex2)

        sorted_data = dict(sorted(self.spot_to_spot_comparison_results.items(), key=lambda item: item[1]['spread'], reverse=True))

        return sorted_data


    def compare_spot_to_spot_by_name(self, spot_exchange_name1, spot_exchange_name2):
        list1 = self.all_possible_spot_prices[spot_exchange_name1].keys()
        list2 = self.all_possible_spot_prices[spot_exchange_name2].keys()

        intersection = list(set(list1).intersection(set(list2)))

        exchange_1 = get_exchange_client_by_exchange_name(self, spot_exchange_name1)
        exchange_2 = get_exchange_client_by_exchange_name(self, spot_exchange_name2)

        for symbol in intersection:
            a = self.all_possible_spot_prices[spot_exchange_name1][symbol]
            b = self.all_possible_spot_prices[spot_exchange_name2][symbol]

            if a is None or b is None:
                print('WRONG SYMBOL, EXCHANGE DOESN"T HAVE SUCH:')
                print(a)
                print(b)
                print(symbol)
                print(spot_exchange_name1)
                print(spot_exchange_name2)
                continue

            key_str = f"{spot_exchange_name1.strip():<10} S  to     {spot_exchange_name2.strip():<10} S - {symbol.strip():<20}"
            self.spot_to_spot_comparison_results[key_str] = {'spread': get_spread(a, b),
                                                             'first_exchange_name': spot_exchange_name1.strip(),
                                                             'second_exchange_name': spot_exchange_name2.strip(),
                                                             'symbol': symbol.strip(),
                                                             'price1': a,
                                                             'price2': b,
                                                             'funding_rate_1': 0,
                                                             'funding_rate_2': 0,
                                                             'funding_gain': 0,
                                                             'spot_futures_comparison': False,
                                                             'spot_spot_comparison': True,
                                                             'execution_spread_loss_1': exchange_1.get_execution_spread_percent(
                                                                 symbol, x_to_x_type='s_to_s') or 0,
                                                             'execution_spread_loss_2': exchange_2.get_execution_spread_percent(
                                                                 symbol, x_to_x_type='s_to_s') or 0,
                                                             }


    def prepare_sorted_data_for_interface(self):
        spot_to_spot_sorted_data_by_spread = self.compare_spot_to_spot_all_to_all()


        spot_to_futures_sorted_data_by_spread = self.compare_spot_to_futures_all_to_all()
        spot_to_futures_sorted_data_by_funding_gain = self.compare_spot_to_futures_all_to_all(by_spread=False)


        sorted_data_by_spread = self.compare_all_to_all()
        sorted_data_by_funding_gain = self.compare_all_to_all(by_spread=False)

        sorted_data = {}

        for k, v in list(sorted_data_by_spread.items())[:consts.LIMITATION_BY_GROUP]:
            sorted_data[f"{k} by_spread"] = v

        for k, v in list(sorted_data_by_funding_gain.items())[:consts.LIMITATION_BY_GROUP]:
            sorted_data[f"{k} by_funding_gain"] = v

        for k, v in list(spot_to_futures_sorted_data_by_spread.items())[:consts.LIMITATION_BY_GROUP]:
            sorted_data[f"{k} s_to_f_comparison_spread"] = v

        for k, v in list(spot_to_futures_sorted_data_by_funding_gain.items())[:consts.LIMITATION_BY_GROUP]:
            sorted_data[f"{k} s_to_f_comparison_funding_gain"] = v

        for k, v in list(spot_to_spot_sorted_data_by_spread.items())[:consts.LIMITATION_BY_GROUP*4]:
            sorted_data[f"{k} s_to_s_comparison_spread"] = v


        short_dict_for_interface = {}
        for key, value in list(sorted_data.items()):
            if consts.FILTER_BY_ONLY_TICKER and consts.FILTER_BY_ONLY_TICKER not in key:
                continue

            short_dict_for_interface[f"🔹 {key}"] = value

        return short_dict_for_interface



