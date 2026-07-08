import ccxt
import time

import consts
from markets_cache import get_markets_with_cache
import threading


from datetime import datetime, timedelta, timezone

from utils import update_symbol_for_specific_exchange_if_needed, get_funding_rate_interval


class ExchangeClient():

    exchange_name = None
    exchange = None
    markets = None
    futures_symbols_dict = None
    futures_symbols = None
    tickers = None
    current_prices = {}
    funding_rates_dict = None
    current_funding_rates = {}
    current_funding_intervals = {}
    spot_symbols_dict = {}
    spot_tickers = None
    spot_current_prices = {}

    cached_order_books = {}
    cached_order_books_cooldown = None

    def __init__(self, exchange_name=None):
        self.exchange_name = exchange_name
        self.exchange = getattr(ccxt, self.exchange_name)({'enableRateLimit': True})

        # self.markets = self.exchange.load_markets()
        self.markets = get_markets_with_cache(self.exchange)


    def get_price(self, symbol=None):
        if not symbol:
            print('wrong args')
            return

        try:
            exchange_ticker = self.exchange.fetch_ticker(symbol)
            print(exchange_ticker['ask'], exchange_ticker['bid'])
        except:
            print(f"Got problems with {self.exchange_name}")


    def get_prices(self, symbols):
        def background_task(is_background=False):
            """Этот метод будет работать в отдельном потоке."""
            # print(f" background_task get_prices", is_background)

            prepared_current_prices = {}
            prepared_tickers = self.exchange.fetch_tickers(symbols, )

            # Выводим цену для нужного списка
            for symbol in symbols:
                if symbol in prepared_tickers:
                    price = prepared_tickers[symbol]['last']
                    # print(f"{symbol}: {price}")
                    prepared_current_prices[symbol] = price

            self.tickers = prepared_tickers
            self.current_prices = prepared_current_prices
            # print('current_prices', len(self.current_prices.keys()))
            # print(f" background_task get_prices FINISHED")


        if self.tickers is None or not self.current_prices:  # if they are none means we are running for the first time.
                                                             # So don't use threading.
                                                             # We need some data to work with in other parts of the program.
            background_task()
        else:  # we can update everything in background
            thread = threading.Thread(
                target=background_task, args=(True,)
            )
            thread.start()


    def get_spot_prices(self, symbols):
        def background_task(is_background=False):
            """Этот метод будет работать в отдельном потоке."""
            # print(f" background_task get_prices", is_background)

            prepared_spot_current_prices = {}
            prepared_spot_tickers = self.exchange.fetch_tickers(symbols, )

            # Выводим цену для нужного списка
            for symbol in symbols:
                if symbol in prepared_spot_tickers:
                    price = prepared_spot_tickers[symbol]['last']
                    # print(f"{symbol}: {price}")
                    prepared_spot_current_prices[symbol] = price

            self.spot_tickers = prepared_spot_tickers
            self.spot_current_prices = prepared_spot_current_prices
            # print('current_prices', len(self.current_prices.keys()))
            # print(f" background_task get_prices FINISHED")


        if self.spot_tickers is None or not self.spot_current_prices:  # if they are none means we are running for the first time.
                                                                         # So don't use threading.
                                                                         # We need some data to work with in other parts of the program.
            background_task()
        else:  # we can update everything in background
            thread = threading.Thread(
                target=background_task, args=(True,)
            )
            thread.start()



    def get_execution_spred_from_order_book(self, symbol):
        def background_task():
            self.cached_order_books[symbol] = self.exchange.fetch_order_book(symbol)

        if self.cached_order_books_cooldown and time.time() - self.cached_order_books_cooldown < 2:
            pass
            # print('REFRESH ORDERBOOK COOLDOWN')
        else:
            thread = threading.Thread(
                target=background_task,)
            thread.start()
            self.cached_order_books_cooldown = time.time()

        if self.cached_order_books.get(symbol):
            orderbook = self.cached_order_books[symbol]
            best_bid = orderbook['bids'][0][0] if orderbook['bids'] else None
            best_ask = orderbook['asks'][0][0] if orderbook['asks'] else None
            if not best_bid or not best_ask:
                return
            return best_ask - best_bid

    def get_execution_spread(self, symbol, x_to_x_type=None):
        if x_to_x_type == 's_to_s' or x_to_x_type == 's_to_f':
            if symbol in self.spot_tickers:
                bid = self.spot_tickers[symbol]['bid']
                ask = self.spot_tickers[symbol]['ask']

                if not bid or not ask:
                    return self.get_execution_spred_from_order_book(symbol)

                return ask - bid
            return


        if symbol in self.tickers:
            bid = self.tickers[symbol]['bid']
            ask = self.tickers[symbol]['ask']

            if not bid or not ask:
                return self.get_execution_spred_from_order_book(symbol)

            return ask - bid

    def get_execution_spread_percent(self, symbol, x_to_x_type=None):
        execution_spread = self.get_execution_spread(symbol, x_to_x_type)

        price = None

        if execution_spread and not x_to_x_type:
            price = self.tickers[symbol]['last']
        elif execution_spread and x_to_x_type == 's_to_s':
            price = self.spot_tickers[symbol]['last']
        elif execution_spread and x_to_x_type == 's_to_f':
            price = self.spot_tickers[symbol]['last']

        if not price:
            return

        return round(execution_spread/price * 100, 6)


    def get_funding_rates(self, symbols):
        # print('GETTING FUNDINGS', self.exchange_name)

        def background_task(is_background=False):
            # print(f" background_task get_funding_rates", is_background)
            prepared_current_funding_rates = {}
            prepared_current_funding_intervals = {}
            try:
                prepared_funding_rates = self.exchange.fetch_funding_rates(symbols, )

                for symbol in symbols:
                    if symbol in prepared_funding_rates:
                        rate = prepared_funding_rates[symbol].get('fundingRate')
                        prepared_current_funding_rates[symbol] = rate
                        # print(f"{symbol}: {rate} (или {rate * 100:.4f}%)")

                        interval = prepared_current_funding_intervals[symbol] = get_funding_rate_interval(prepared_funding_rates[symbol])

                        if interval == '4h':
                            prepared_current_funding_rates[symbol] = rate * 2
                        if interval == '1h':
                            prepared_current_funding_rates[symbol] = rate * 8

                        # print("interval")
                        # print(interval)

            except Exception as e:
                for symbol in symbols:
                    if symbol in self.tickers:
                        rate = self.tickers[symbol]['info'].get('fundingRate')

                        if not rate:
                            rate = self.tickers[symbol]['info'].get('fundingFeeRate')

                        if not rate:
                            continue

                        prepared_current_funding_rates[symbol] = rate
                        # print(f"{symbol}: {rate} (или {float(rate) * 100}%)")

                        interval = prepared_current_funding_intervals[symbol] = get_funding_rate_interval(self.tickers[symbol]['info'])

                        if interval == '4h':
                            prepared_current_funding_rates[symbol] = rate * 2
                        if interval == '1h':
                            prepared_current_funding_rates[symbol] = rate * 8
                        # print("interval")
                        # print(interval)


            self.current_funding_rates = prepared_current_funding_rates
            self.current_funding_intervals = prepared_current_funding_intervals
            # print(self.current_funding_rates)
            # print(f" background_task get_funding_rates FINISHED")

        if not self.current_funding_rates:  # if they are none means we are running for the first time.
            # So don't use threading.
            # We need some data to work with in other parts of the program.
            background_task()
        else:  # we can update everything in background
            thread = threading.Thread(
                target=background_task, args=(True,)
            )
            thread.start()

    def get_all_futures_symbols(self, ):
        # Получаем список всех доступных futures
        self.futures_symbols_dict = {symbol: market for symbol, market in self.markets.items() if (market.get('swap') or market.get('future')) and "USDT" in symbol and symbol[-4:] == "USDT"}

        # maybe should be refactored for dex

    def get_all_spot_symbols(self, ):
        # Получаем список всех доступных символов
        fiat_currencies = {'EUR', 'TRY', 'AED', 'USD', 'RUB', 'GBP', 'UAH'}
        #
        # self.spot_symbols_dict = {symbol: market for symbol, market in self.markets.items() if not ("USDT" in symbol and symbol[-4:] == "USDT")}
        self.spot_symbols_dict = {symbol: market for symbol, market in self.markets.items() if market['type'] == 'spot' and market['active'] and market['quote'] not in fiat_currencies}
        # self.spot_symbols_dict = {symbol: market for symbol, market in self.markets.items() if not(market.get('swap') or market.get('future')) and market['active']}
        # print(self.spot_symbols_dict.keys())


    def refresh_prices_and_fundings(self):
        self.get_all_futures_symbols()
        self.get_prices(list(self.futures_symbols_dict.keys()))
        self.get_funding_rates(list(self.futures_symbols_dict.keys()))


        self.get_all_spot_symbols()
        self.get_spot_prices(list(self.spot_symbols_dict.keys()))



    def fetch_multiple_ohlcv(self, symbol="BTC/USDT", timeframe='1m', limit=500, days_ago=2, s_to_f=None,s_to_s=None,):
        symbol = update_symbol_for_specific_exchange_if_needed(self.exchange_name,
                                                               symbol,
                                                               s_to_f=s_to_f,
                                                               s_to_s=s_to_s,)

        # Определяем точку старта (10 дней назад от текущего момента)
        start_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
        since_timestamp = int(start_date.timestamp() * 1000)

        all_ohlcv = []

        print(f"Начинаем загрузку данных c {self.exchange_name} для {symbol} с {start_date}...")

        # 3. Цикл для пагинации данных
        retry = False
        now_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        last_timestamp = since_timestamp
        while True:
            try:
                # print("now_timestamp")
                # print(now_timestamp)
                if since_timestamp > now_timestamp:
                    print("Достигли текущего времени (в будущем).")
                    break


                # Получаем порцию данных
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol, timeframe, since=since_timestamp, limit=limit
                )

                # if not ohlcv:
                #     print("Все доступные данные успешно загружены.")
                #     break

                # Добавляем полученные свечи в общий список
                all_ohlcv.extend(ohlcv)

                # Берем таймстамп последней полученной свечи
                try:
                    if last_timestamp == ohlcv[-1][0]:
                        # data is not changing, breaking loop
                        break

                    last_timestamp = ohlcv[-1][0]
                    # last_timestamp += 60000
                    # print('here1')


                except:
                    last_timestamp += limit * 60000
                    # print('here2')

                # print('last_timestamp', last_timestamp)
                since_timestamp = last_timestamp
                # print('since_timestamp', since_timestamp)
                # Проверяем, не дошли ли мы до самого свежего момента
                # Если биржа вернула меньше данных, чем лимит, значит мы в самом конце
                # if len(ohlcv) < limit:
                #     print("Достигли актуального времени.")
                #     break

                # Сдвигаем `since` на 1 минуту вперед от последней свечи для следующей итерации
                # since_timestamp = last_timestamp + 60000
                # print(since_timestamp)

                if since_timestamp >  int(datetime.now(timezone.utc).timestamp() * 1000):
                    print("Превысили актуальное времени.")
                    break

                # Небольшая пауза между запросами для безопасности
                time.sleep(self.exchange.rateLimit / 1000)

            except Exception as e:
                break


        # 4. Агрегация, очистка и сортировка
        # Удаляем дубликаты (используем таймстамп как уникальный ключ)
        unique_ohlcv = {row[0]: row for row in all_ohlcv}.values()
        # Сортируем по возрастанию даты (по первому элементу — таймстампу)
        final_ohlcv = sorted(unique_ohlcv, key=lambda x: x[0])


        if s_to_f and symbol in consts.SPLITTED_IN_TWO:
            for col in ['open', 'high', 'low', 'close', ]:
                final_ohlcv[col] = final_ohlcv[col] / 2

        # import json
        # import re
        # # Сохраняем словарь в файл
        # file_name = f'{self.exchange_name} для {symbol} с {start_date}.json'
        # safe_file_name = re.sub(r'[\/:*?"<>|+\s]', '_', file_name)
        #
        # with open(safe_file_name, 'w', encoding='utf-8') as f:
        #     json.dump(final_ohlcv, f, ensure_ascii=False, indent=4)

        return final_ohlcv






