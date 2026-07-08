import customtkinter as ctk
import webbrowser
from decimal import Decimal

import consts
from ignore_cache import IgnoreCache
from utils import get_exchange_client_by_exchange_name, get_funding_gain, get_spread, \
    get_prepared_dict_for_all_exchanges, get_spread_alerts_and_funding_alerts

ctk.set_appearance_mode("dark")  # "dark", "light", "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class Interface(ctk.CTk):
    colors = [
        "#45B7D1",  # голубой
    ]

    exchange_labels = []
    buttons_list = []

    comparer = None

    ignore_cache = IgnoreCache()

    def __init__(self, lines_dict, comparer):
        super().__init__()

        self.line_dict = lines_dict

        self.comparer = comparer
        self.labels_text = None
        self.exchange_name1 = None
        self.exchange_name2 = None

        self.title("BEST OPTIONS")
        self.geometry("200x200+0+0")
        self.resizable(True, True)

        # Заголовок
        title = ctk.CTkLabel(self, text="CHOOSE OPTION", font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(pady=20)

        self.refresh_btn = ctk.CTkButton(
            self,
            text='REFRESH ALL',
            height=45,
            fg_color='violet',
            hover_color='white',
            text_color="black",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            anchor="w",  # текст слева
            corner_radius=8
        )
        self.refresh_btn.pack(fill="x", pady=6, padx=10)
        self.refresh_btn.configure(command=self.refresh_main_window)

        # Скроллируемая область
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(
            self.scrollable_frame,
            placeholder_text="Поиск...",
            font=ctk.CTkFont(family="Consolas", size=13)
        )
        self.search_entry.pack(fill="x", padx=10, pady=5)

        # Привязка нажатия Enter к функции фильтрации
        self.search_entry.bind("<Return>", self.filter_buttons)

        # Создаём кнопки (полоски)
        self.create_line_buttons(lines_dict)

        self.open_alert_window()

    def filter_buttons(self, event=None):
        # Получаем текст из поля ввода и переводим в нижний регистр
        search_query = self.search_entry.get().upper()

        print("search_query")
        print(search_query)

        for button in self.buttons_list:
            button.destroy()

        self.line_dict

        filtered_line_dict = {
            k:v for k,v in self.line_dict.items() if search_query in k
        }

        self.create_line_buttons(filtered_line_dict)


    def create_line_buttons(self, lines_dict, ):
        border_type = None
        border_type_iterators = ['by_spread',
                                 'by_funding_gain',
                                 's_to_f_comparison_spread',
                                 's_to_f_comparison_funding_gain',
                                 's_to_s_comparison_spread',
                                 'end_of_iterators']
        do_draw_border = False
        for i, line in enumerate(lines_dict.keys()):
            color = self.colors[i % len(self.colors)] if hasattr(self, 'colors') else "#1f538d"

            # printing the border between type of arbitrage opportunities
            for border_type_iterator in border_type_iterators:
                if border_type and border_type in line:
                    do_draw_border = False
                    break

                if border_type is None:
                    border_type = border_type_iterator
                    do_draw_border = True
                    border_type_iterators.remove(border_type)
                    break

                if border_type != border_type_iterator and border_type_iterator in line:
                    do_draw_border = True
                    border_type = border_type_iterator
                    border_type_iterators.remove(border_type)
                    break

            if 'by_spread' in line:
                color = "#45B7D1"
            if 'by_funding_gain' in line:
                color = "#D4A5A5"
            if 's_to_f_comparison_spread' in line:
                color = "purple"
            if 's_to_f_comparison_funding_gain' in line:
                color = "red"

            if 's_to_s_comparison_spread' in line:
                color = "green"


            if do_draw_border:
                btn = ctk.CTkButton(
                    self.scrollable_frame,
                    text=border_type,
                    height=45,
                    fg_color=color,
                    hover_color=self.lighten_color(color),
                    text_color="black",
                    font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
                    anchor="w",  # текст слева
                    corner_radius=8
                )
                btn.pack(fill="x", pady=(20, 5), padx=10)
                self.buttons_list.append(btn)


            line_info = lines_dict[line]

            funding_gain = line_info['funding_gain']
            if 'N\A' in [line_info['funding_rate_1'], line_info['funding_rate_2']]:
                funding_gain = 'N\A'
                fr1 = f"{Decimal(line_info['funding_rate_1']) * 100:.5f}" if line_info['funding_rate_1'] != 'N\A' else 'N\A'
                fr2 = f"{Decimal(line_info['funding_rate_2']) * 100:.5f}" if line_info['funding_rate_2'] != 'N\A' else 'N\A'
            else:
                fr1 = f"{Decimal(line_info['funding_rate_1']) * 100:.5f}"
                fr2 = f"{Decimal(line_info['funding_rate_2']) * 100:.5f}"
                funding_gain = f"{Decimal(funding_gain):.7f}"

            info_to_show_in_menu_item = f"{line_info['first_exchange_name']:<10} to " \
                                        f"{line_info['second_exchange_name']:<10} - " \
                                        f"{line_info['symbol']:<20} " \
                                        f"p1 {line_info['price1']:<8}  " \
                                        f"p2 {line_info['price2']:<8} " \
                                        f"spread:{line_info['spread']}  " \
                                        f"fr1: {fr1:>8}% " \
                                        f"fr2: {fr2:>8}%  " \
                                        f"fund gain: {funding_gain::>5}% "


            btn = ctk.CTkButton(
                self.scrollable_frame,
                text=info_to_show_in_menu_item,
                height=45,
                fg_color=color,
                hover_color=self.lighten_color(color),
                text_color="black",
                font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
                anchor="w",  # текст слева
                corner_radius=8
            )
            btn.pack(fill="x", pady=6, padx=10)

            # Привязываем клик
            btn.configure(command=lambda c=line: self.on_click(c))
            # print(line)
            self.buttons_list.append(btn)


    def lighten_color(self, color):
        """Небольшой эффект при наведении"""
        return color  # можно улучшить позже

    def on_click(self, choice):
        print(f"Выбрано: {choice}")
        # сюда твой текущий код
        self.open_sub_window(choice)

    def refresh_main_window(self):
        self.refresh_btn.configure(text='DONE REFRESH')

        for button in self.buttons_list:
            button.destroy()

        self.comparer.refresh_all_exchanges_and_prices()
        self.line_dict = self.comparer.prepare_sorted_data_for_interface()

        self.create_line_buttons(self.line_dict)

        self.after(3000, lambda: self.refresh_btn.configure(text='REFRESH'))

    def on_label_click(self, action, line):

        symbol = self.cached_sub_window_line['symbol'].replace(':USDT', '')

        if action == "Локальные графики":
            exchange_client_1 = get_exchange_client_by_exchange_name(self.comparer, self.exchange_name1)
            exchange_client_2 = get_exchange_client_by_exchange_name(self.comparer, self.exchange_name2)

            # print('debug execution spread losses')
            # print(exchange_client_1.get_execution_spread_percent(self.line_dict[line]['symbol']))
            # print(exchange_client_2.get_execution_spread_percent(self.line_dict[line]['symbol']))

            from chart_drawer import draw_all_three_charts

            draw_all_three_charts(exchange_client_1, exchange_client_2, symbol, timeframe='1m', line=self.cached_sub_window_line)

            return

        if action == 'Close all local charts':
            print(f"Выполняю '{action}' с символом '{symbol}'для элемента '{line}'")
            import matplotlib.pyplot as plt

            # Закрывает абсолютно все открытые графики
            plt.close('all')
            return

        if action == 'Trading View 1d spread only':
            print(f"Выполняю '{action}' с символом '{symbol}'для элемента '{line}'")
            symbol_trading_view_repr = symbol.replace('/', '').upper() + '.P'

            'https://www.tradingview.com/chart/?symbol=LBANK%3AKOPNUSDT.P%2FBITGET%3AKOPNUSDT.P'
            url = f'https://www.tradingview.com/chart/' \
                  f'?symbol={self.exchange_name1.upper()}%3A{symbol_trading_view_repr}%2F{self.exchange_name2.upper()}%3A{symbol_trading_view_repr}'
            webbrowser.open(url)

            return

        """Обработчик нажатия на надпись в новом окне"""
        print(f"Выполняю '{action}' с символом '{symbol}'для элемента '{line}'")

        spot_url = consts.SPOT_EXCHANGES_SITES[action] + consts.SPOT_EXCHANGES_SITES_FORMATTERS[action](symbol)
        futures_url = consts.EXCHANGES_SITES[action] + consts.EXCHANGES_SITES_FORMATTERS[action](symbol)

        if self.cached_sub_window_line.get('spot_spot_comparison'):
            url = spot_url

        elif self.cached_sub_window_line.get('spot_futures_comparison'):
            if self.exchange_name1 == action:  # we need spot url
                url = spot_url
            else:                              # we need spot url
                url = futures_url

        else:
            url = futures_url
        webbrowser.open(url)

    def set_to_ignore_alert(self, line):
        self.ignore_cache.put(line)
        if hasattr(self, 'child_window') and self.child_window is not None and self.child_window.winfo_exists():
            self.child_window.destroy()  # Закрываем старое окно

    def set_to_ignore_alert_forever(self, line):
        self.ignore_cache.ignore_forever(line)
        self.set_to_ignore_alert(line)


    def open_sub_window(self, choice):
        """Метод для создания и позиционирования нового окна рядом"""
        self.cached_sub_window_choice = choice
        self.cached_sub_window_line = self.line_dict.get(choice)

        # print('debug')
        # print(self.line_dict)
        # print(choice)

        if not self.cached_sub_window_line:
            return

        # Создаем новое окно
        if hasattr(self, 'child_window') and self.child_window is not None and self.child_window.winfo_exists():
            self.child_window.destroy()  # Закрываем старое окно

        self.child_window = ctk.CTkToplevel(self)
        self.child_window.title(f"Опции для: {choice}")
        self.child_window.geometry("500x700")

        # Поверх основного окна
        self.child_window.attributes("-topmost", True)

        # Вычисляем координаты, чтобы открыть окно СПРАВА от главного
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()

        # Смещаем новое окно вправо на ширину главного + 10 пикселей отступа
        new_x = main_x + main_width + 10
        new_y = main_y

        self.child_window.geometry(f"+{new_x}+{new_y}")

        btn = ctk.CTkButton(
            self.child_window,
            text='IGNORE ALERT',
            height=45,
            fg_color='white',
            hover_color='blue',
            text_color="black",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            anchor="w",
            corner_radius=8
        )
        btn.configure(command=lambda c=self.cached_sub_window_line: self.set_to_ignore_alert(c))
        btn.pack(pady=5, padx=10, fill="x")

        btn = ctk.CTkButton(
            self.child_window,
            text='IGNORE FOREWER',
            height=45,
            fg_color='red',
            hover_color='black',
            text_color="black",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            anchor="w",
            corner_radius=8
        )
        btn.configure(command=lambda c=self.cached_sub_window_line: self.set_to_ignore_alert_forever(c))
        btn.pack(pady=5, padx=10, fill="x")


        self.exchange_name1 = self.cached_sub_window_line['first_exchange_name']  # Индекс 0
        self.exchange_name2 = self.cached_sub_window_line['second_exchange_name']  # Индекс 2

        exchange_client_1 = get_exchange_client_by_exchange_name(self.comparer, self.exchange_name1)
        exchange_client_2 = get_exchange_client_by_exchange_name(self.comparer, self.exchange_name2)

        if 'gate' in [self.exchange_name1, self.exchange_name2]:
            gate_warning = ctk.CTkLabel(
                self.child_window,
                text='WARNING: DONT SHORT ON GATE EX. SPIKE WARNING.',
                font=ctk.CTkFont(size=14, underline=False),  # Подчеркивание для имитации ссылки
            )
            gate_warning.pack(pady=15)



        self.labels_text = [self.exchange_name1,
                            self.exchange_name2,
                            "Локальные графики",
                            "Close all local charts",
                            'Trading View 1d spread only',]

        for text in self.labels_text:
            lbl = ctk.CTkLabel(
                self.child_window,
                text=text,
                font=ctk.CTkFont(size=14, underline=True),  # Подчеркивание для имитации ссылки
                cursor="hand2"  # Курсор-рука при наведении
            )
            lbl.pack(pady=15)

            # Привязываем клик левой кнопкой мыши (<Button-1>)
            # Использование lambda с аргументом t=text сохраняет нужное значение для каждого цикла
            lbl.bind("<Button-1>", lambda event, t=text: self.on_label_click(t, choice))

        self.info_spread = ctk.CTkLabel(
            self.child_window,
            text='Real spread: ',
            font=ctk.CTkFont(size=14, underline=False),  # Подчеркивание для имитации ссылки
        )
        self.info_spread.pack(pady=15)

        self.info_funding_gain = ctk.CTkLabel(
            self.child_window,
            text='Real funding gain (per each period 1-4-8h): ',
            font=ctk.CTkFont(size=14, underline=False),  # Подчеркивание для имитации ссылки
        )
        self.info_funding_gain.pack(pady=15)


        self.symbol =self.cached_sub_window_line['symbol']

        x_to_x_type = None

        if self.cached_sub_window_line.get('spot_spot_comparison'):
            x_to_x_type = 's_to_s'

        if self.cached_sub_window_line.get('spot_futures_comparison'):
            x_to_x_type = 's_to_f'

        spread_loss1 = exchange_client_1.get_execution_spread_percent(self.symbol, x_to_x_type=x_to_x_type) or 'N/A'


        if self.cached_sub_window_line.get('spot_futures_comparison'):
            x_to_x_type = None
            self.symbol = self.cached_sub_window_line['futures_symbol']

        spread_loss2 = exchange_client_2.get_execution_spread_percent(self.symbol, x_to_x_type=x_to_x_type) or 'N/A'

        # print(spread_loss1, spread_loss2)

        self.execution_spread_losses = ctk.CTkLabel(
            self.child_window,
            text=f'Execution spread losses (divide by 2 per each leg): {spread_loss1}%, {spread_loss2}%',
            font=ctk.CTkFont(size=14, underline=False),  # Подчеркивание для имитации ссылки
        )
        self.execution_spread_losses.pack(pady=15)


        # MAX DELTA SEARCH
        # MAX DELTA SEARCH
        # MAX DELTA SEARCH
        exchange_client_1 = get_exchange_client_by_exchange_name(self.comparer, self.exchange_name1)
        exchange_client_2 = get_exchange_client_by_exchange_name(self.comparer, self.exchange_name2)
        prepared_dict = get_prepared_dict_for_all_exchanges(self.comparer, self.symbol, [exchange_client_1, exchange_client_2])

        self.exchange_labels = []
        for k, v in prepared_dict.items():
            current_price = v["current_price"]
            average = v["average"]
            delta = v["delta"]

            info_label_for_exchange = ctk.CTkLabel(
                self.child_window,
                text=f'Exchange {k:<10}: price: {current_price:>10} average: {average:>10} delta: {delta:>10}',
                font=ctk.CTkFont(size=14, underline=False),  # Подчеркивание для имитации ссылки
            )
            info_label_for_exchange.pack(pady=15)
            self.exchange_labels.append(info_label_for_exchange)

        self.update_sub_window_info(choice)

    def update_sub_window_info(self, choice):
        if not hasattr(self, 'child_window') or not self.child_window.winfo_exists():
            return  # Окно закрыто — прекращаем рекурсию


        exchange_client_1 = get_exchange_client_by_exchange_name(self.comparer, self.exchange_name1)
        exchange_client_2 = get_exchange_client_by_exchange_name(self.comparer, self.exchange_name2)

        self.comparer.refresh_current_exchange(exchange_client_1)
        self.comparer.refresh_current_exchange(exchange_client_2)

        # === Здесь обновляем информацию ===
        first_exchange_name = self.cached_sub_window_line['first_exchange_name']
        second_exchange_name = self.cached_sub_window_line['second_exchange_name']
        symbol = self.cached_sub_window_line['symbol']

        spot_symbol = self.cached_sub_window_line['spot_symbol'] if self.cached_sub_window_line.get('spot_futures_comparison') else None
        futures_symbol = self.cached_sub_window_line['futures_symbol'] if self.cached_sub_window_line.get('spot_futures_comparison') else None

        x_to_x_type = None

        if self.cached_sub_window_line.get('spot_spot_comparison'):
            x_to_x_type = 's_to_s'

        if self.cached_sub_window_line.get('spot_futures_comparison'):
            x_to_x_type = 's_to_f'



        spread_loss1 = exchange_client_1.get_execution_spread_percent(symbol, x_to_x_type) or 'N/A'

        if self.cached_sub_window_line.get('spot_futures_comparison'):
            x_to_x_type = None
            symbol = self.cached_sub_window_line['futures_symbol']

        spread_loss2 = exchange_client_2.get_execution_spread_percent(symbol, x_to_x_type) or 'N/A'
        self.execution_spread_losses.configure(text=f'Execution spread losses (divide by 2 for each leg): {spread_loss1}%, {spread_loss2}%')

        '''
        а это всегда спот
        б это всегда фьюч
        '''
        if self.cached_sub_window_line.get('spot_spot_comparison'):
            a = self.comparer.all_possible_spot_prices[first_exchange_name][symbol]
            b = self.comparer.all_possible_spot_prices[second_exchange_name][symbol]

        elif not self.cached_sub_window_line.get('spot_futures_comparison'):                 # F - F
            a = self.comparer.all_possible_prices[first_exchange_name][symbol]
            b = self.comparer.all_possible_prices[second_exchange_name][symbol]
        else:                                                                              # S - F
            a = self.comparer.all_possible_spot_prices[first_exchange_name][spot_symbol]
            b = self.comparer.all_possible_prices[second_exchange_name][futures_symbol]


        if a is None or b is None:
            print('WRONG SYMBOL, EXCHANGE DOESN"T HAVE SUCH:')
            print(a)
            print(b)
            print(symbol)
            print(first_exchange_name)
            print(second_exchange_name)
            return

        if not self.cached_sub_window_line.get('spot_futures_comparison'): # F - F
            a_funding = self.comparer.all_possible_funding_rates[first_exchange_name].get(symbol)

            if a_funding is None:
                a_funding = 'N\A'

            b_funding = self.comparer.all_possible_funding_rates[second_exchange_name].get(symbol) or 'N\A'

            if b_funding is None:
                b_funding = 'N\A'
        else:
            a_funding = 0
            b_funding = self.comparer.all_possible_funding_rates[second_exchange_name].get(symbol+':USDT') or 'N\A'

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

        try:
            self.info_spread.configure(text=f'Real spread: {get_spread(a, b):.5f}')
            self.info_funding_gain.configure(text=f'Real funding gain (per each period 1-4-8h): {funding_gain:.5f}%')

            if funding_gain == -99999:
                self.info_funding_gain.pack_forget()

        except Exception as e:
            # На случай ошибки (например, если данные не удалось получить)
            self.info_spread.configure(text=f"Ошибка обновления:\n{str(e)}")

        prepared_dict = get_prepared_dict_for_all_exchanges(self.comparer, self.symbol, [exchange_client_1, exchange_client_2])

        label_cnt = 0
        for k, v in prepared_dict.items():
            current_price = v["current_price"]
            average = v["average"]
            delta = v["delta"]
            info_label_for_exchange = self.exchange_labels[label_cnt]
            label_cnt += 1
            info_label_for_exchange.configure(text=f'Exchange {k:<10}: price: {current_price:>10} average: {average:>10} delta: {delta:>10}')


        self.child_window.after(3000, self.update_sub_window_info, choice)


    def open_alert_window(self, ):
        self.child_alert_window = ctk.CTkToplevel(self)
        self.child_alert_window.title(f"ALERTS")
        self.child_alert_window.geometry("700x600")
        self.child_alert_window.attributes("-topmost", False)
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        new_x = main_x + main_width + 10
        new_y = main_y
        self.child_alert_window.geometry(f"+{new_x}+{new_y}")
        self.alert_scrollable_frame = ctk.CTkScrollableFrame(
            self.child_alert_window,
            fg_color="transparent"
        )
        self.alert_scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.alert_buttons = []
        self.after(100, self.refresh_alert_window)

    def refresh_alert_window(self, ):
        if not hasattr(self, 'child_alert_window') or not self.child_alert_window.winfo_exists():
            return

        self.comparer.refresh_all_exchanges_and_prices()
        self.line_dict = self.comparer.prepare_sorted_data_for_interface()

        for button in self.alert_buttons:
            button.destroy()

        spread_alerts, \
        funding_alerts, \
        spot_to_futures_spread_alerts, \
        spot_to_futures_funding_alerts, \
        spot_to_spot_alerts = get_spread_alerts_and_funding_alerts(self.line_dict,
                                                                   self.ignore_cache)

        if spread_alerts:
            self.draw_alert_separator(name='f to f spread')
            self.draw_alerts(spread_alerts)

        if funding_alerts:
            self.draw_alert_separator(name='f to f funding', b_color='white')
            self.draw_alerts(funding_alerts, b_color='white')

        if spot_to_futures_spread_alerts:
            self.draw_alert_separator(name='s to f spread', b_color='pink')
            self.draw_alerts(spot_to_futures_spread_alerts, b_color='pink')

        if spot_to_futures_funding_alerts:
            self.draw_alert_separator(name='s to f funding', b_color='grey')
            self.draw_alerts(spot_to_futures_funding_alerts, b_color='grey')

        if spot_to_spot_alerts:
            self.draw_alert_separator(name='s to s spread', b_color='antique white')
            self.draw_alerts(spot_to_spot_alerts, b_color='antique white')

        self.after(30000, self.refresh_alert_window)

    def draw_alerts(self, list_of_alerts, b_color='yellow'):
        if list_of_alerts and consts.SOUND_ON:  # sound only for spreads
            import ctypes
            ctypes.windll.winmm.mciSendStringW("play sounds/Alarm01.wav", None, 0, None)
            # print('SOUND !!!!!!!!!!!!!!!!!  list_of_alerts', list_of_alerts)

        for text in list_of_alerts.keys():
            # Строка
            v = list_of_alerts[text]
            prepared_text = f"{v['first_exchange_name']} to {v['second_exchange_name']} {v['symbol']} spread {v['spread']}"

            if v['funding_gain']:
                prepared_text += f" fund {v['funding_gain']:.4f}"

            if 'execution_spread_loss_1' in v.keys() and 'execution_spread_loss_2' in v.keys():
                prepared_text += f" ex.l: {v['execution_spread_loss_1']:.4f}% ex.l:  {v['execution_spread_loss_2']:.4f}%"

            # Кнопка
            btn = ctk.CTkButton(
                self.alert_scrollable_frame,
                text=prepared_text,
                height=45,
                fg_color=b_color,
                hover_color='red',
                text_color="black",
                font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
                anchor="w",
                corner_radius=8
            )
            btn.configure(command=lambda c=text: self.on_click(c))
            btn.pack(pady=5, padx=10, fill="x")
            self.alert_buttons.append(btn)

    def draw_alert_separator(self, name, b_color='yellow'):
        prepared_text = name
        btn = ctk.CTkButton(
            self.alert_scrollable_frame,
            text=prepared_text,
            height=45,
            fg_color=b_color,
            text_color="black",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            anchor="w",
            corner_radius=8
        )
        btn.pack(pady=(20, 5), padx=10, fill="x")
        self.alert_buttons.append(btn)










