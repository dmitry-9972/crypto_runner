import logging
import pandas as pd
import mplfinance as mpf

import matplotlib.pyplot as plt

logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)


class ChartDrawer:
    ohlcv = None
    ohlcv1 = None
    ohlcv2 = None
    chart_name = None

    def __init__(self, ohlcv1=None, ohlcv2=None, chart_name="Chart"):

        self.ohlcv = ohlcv1
        self.ohlcv1 = ohlcv1
        self.ohlcv2 = ohlcv2
        self.chart_name = chart_name


    def draw(self):

        df = pd.DataFrame(self.ohlcv, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = df['date'] // 1000
        df['date'] = pd.to_datetime(df['date'], unit='s')
        df = df.set_index('date')

        fig, _ = mpf.plot(df,
                          type='candle',
                          volume=True,
                          style='binance',
                          # title=self.chart_name,
                          tight_layout=True,
                          figsize=(5, 3),
                          xrotation=90,
                          warn_too_much_data=100000,
                          returnfig=True,
                          block=False)

        fig.canvas.manager.set_window_title(self.chart_name)
        plt.show(block=False)

    def draw_spread(self, ):

        if not all((self.ohlcv1, self.ohlcv2)):
            print('NOT ALL ARGS PASSED')
            return

        df1 = pd.DataFrame(self.ohlcv1, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df2 = pd.DataFrame(self.ohlcv2, columns=['date', 'open', 'high', 'low', 'close', 'volume'])

        common_dates = pd.merge(
            df1[['date']],
            df2[['date']],
            on='date',
            how='inner'
        )['date']

        df1 = df1[df1['date'].isin(common_dates)].reset_index(drop=True)
        df2 = df2[df2['date'].isin(common_dates)].reset_index(drop=True)

        spread_df = df1[['date']].copy()  # берём дату из первого

        import numpy as np
        for col in ['open', 'high', 'low', 'close', 'volume']:
            spread_df[col] = df1[col] / df2[col]
            spread_df[col] = spread_df[col].replace([np.inf, -np.inf], np.nan)

        df = spread_df
        # for index, row in df.iterrows():
        #     print(index, row)

        df['date'] = df['date'] // 1000
        df['date'] = pd.to_datetime(df['date'], unit='s')
        df = df.set_index('date')

        fig, axlist = mpf.plot(df,
                               type='candle',
                               volume=True,
                               style='binance',
                               # title=self.chart_name,
                               figsize=(7, 4),
                               xrotation=90,
                               tight_layout=True,
                               warn_too_much_data=100000,
                               returnfig=True,
                               block=True)

        fig.canvas.manager.set_window_title(self.chart_name)
        plt.show(block=False)


    def draw_spread_only_close_price(self, ):

        if not all((self.ohlcv1, self.ohlcv2)):
            print('NOT ALL ARGS PASSED')
            return

        df1 = pd.DataFrame(self.ohlcv1, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df2 = pd.DataFrame(self.ohlcv2, columns=['date', 'open', 'high', 'low', 'close', 'volume'])

        common_dates = pd.merge(
            df1[['date']],
            df2[['date']],
            on='date',
            how='inner'
        )['date']

        df1 = df1[df1['date'].isin(common_dates)].reset_index(drop=True)
        df2 = df2[df2['date'].isin(common_dates)].reset_index(drop=True)

        # spread_df = df1[['date']].copy()  # берём дату из первого

        # for col in ['open', 'high', 'low', 'close', 'volume']:
        #     spread_df[col] = df1[col] / df2[col]
        #     spread_df[col] = spread_df[col].replace([np.inf, -np.inf], np.nan)

        # df = spread_df
        # for index, row in df.iterrows():
        #     print(index, row)

        df1['date'] = df1['date'] // 1000
        df1['date'] = pd.to_datetime(df1['date'], unit='s')
        df1 = df1.set_index('date')

        df2['date'] = df2['date'] // 1000
        df2['date'] = pd.to_datetime(df2['date'], unit='s')
        df2 = df2.set_index('date')

        # fig, axlist = mpf.plot(df,
        #                        type='candle',
        #                        volume=True,
        #                        style='binance',
        #                        # title=self.chart_name,
        #                        figsize=(7, 4),
        #                        xrotation=90,
        #                        tight_layout=True,
        #                        warn_too_much_data=100000,
        #                        returnfig=True,
        #                        block=True)

        # fig.canvas.manager.set_window_title(self.chart_name)

        ap = [
            mpf.make_addplot(df1['close'], color='#2196F3', width=0.5, label='df1 Close'),
            mpf.make_addplot(df2['close'], color='#FF9800', width=0.5, label='df2 Close')
        ]

        # Используем любой из df как основу (они одинаковые по индексу)
        mpf.plot(df1,
                 type='line',
                 style='binance',
                 addplot=ap,
                 figsize=(7, 4),
                 xrotation=90,
                 tight_layout=True,
                 title=self.chart_name,
                 block=True)

        plt.show(block=False)

def draw_all_three_charts(exchange_client_1, exchange_client_2, symbol_inner_representation, timeframe='1h', line=None):
    # print("line")
    # print(line)


    # эти услови нужны чтоб понять где какой символ качать. спотовый - без :юсдт или фьючерсный с юсдт
    s_to_f = None
    s_to_s = None

    if line.get('spot_futures_comparison') and exchange_client_1.exchange_name == line.get('spot_exchange_name'):
        s_to_f = True

    if line.get('spot_futures_comparison') and exchange_client_1.exchange_name == line.get('futures_exchange_name'):
        s_to_f = False

    # но если мы работаем с одной и той же биржей, то нам надо вручную забить что и откуда брать
    if line.get('spot_futures_comparison') and exchange_client_1.exchange_name == exchange_client_2.exchange_name:
        s_to_f = False

    if line.get('spot_spot_comparison'):
        s_to_s = True

    # if line.get('spot_futures_comparison') and exchange_client_1.exchange_name != line.get('futures_exchange_name'):
    #     print('EXCHANGE NAME MISMATCH 1')

    ohlcv1 = exchange_client_1.fetch_multiple_ohlcv(symbol_inner_representation, timeframe, limit=500, s_to_f=s_to_f, s_to_s=s_to_s)

    if ohlcv1:
        drawer = ChartDrawer(ohlcv1, chart_name=f"{exchange_client_1.exchange_name} {symbol_inner_representation}")
        drawer.draw()
    else:
        print('NO DATA FOR', symbol_inner_representation, exchange_client_1.exchange_name)

    s_to_f = None
    if line.get('spot_futures_comparison') and exchange_client_2.exchange_name == line.get('spot_exchange_name'):
        s_to_f = True

    if line.get('spot_futures_comparison') and exchange_client_2.exchange_name == line.get('futures_exchange_name'):
        s_to_f = False

    if line.get('spot_futures_comparison') and exchange_client_1.exchange_name == exchange_client_2.exchange_name:
        s_to_f = True

    ohlcv2 = exchange_client_2.fetch_multiple_ohlcv(symbol_inner_representation, timeframe, limit=500, s_to_f=s_to_f, s_to_s=s_to_s)

    if ohlcv2:
        drawer = ChartDrawer(ohlcv2, chart_name=f"{exchange_client_2.exchange_name} {symbol_inner_representation}")
        drawer.draw()
    else:
        print('NO DATA FOR', symbol_inner_representation, exchange_client_2.exchange_name)

    if all((ohlcv1, ohlcv2)):
        drawer = ChartDrawer(ohlcv1, ohlcv2, chart_name=f'{symbol_inner_representation} {exchange_client_1.exchange_name}/{exchange_client_2.exchange_name}')
        drawer.draw_spread()
        drawer.draw_spread_only_close_price()
    else:
        print('NO DATA FOR', symbol_inner_representation, exchange_client_1.exchange_name, exchange_client_2.exchange_name)


# exchange = ccxt.gate()
# ohlcv1 = exchange.fetch_ohlcv('BP/USDT:USDT', '15m', limit=500)
# drawer = ChartDrawer(ohlcv1, chart_name='ByBit BP/USDT')
# drawer.draw()
#
# exchange = ccxt.mexc()
# ohlcv2 = exchange.fetch_ohlcv('STG/USDT:USDT', '15m', limit=500)
# drawer = ChartDrawer(ohlcv2, chart_name='mexc BP/USDT')
# drawer.draw()
#
# drawer = ChartDrawer(ohlcv1, ohlcv2, chart_name='STG/USDT:USDT mexc/ByBit')
# drawer.draw_spread()



# from client import ExchangeClient
#
# print('testing with', 'lbank')
# exchange_client = ExchangeClient('lbank')
# exchange_client.get_all_futures_symbols()
# 'ANTHROPIC/USDT:USDT'
# exchange_client.get_prices(list(exchange_client.futures_symbols_dict.keys()))
# print(exchange_client.current_prices['ANTHROPIC/USDT:USDT'])
# print(exchange_client.markets['ANTHROPIC/USDT:USDT'])

