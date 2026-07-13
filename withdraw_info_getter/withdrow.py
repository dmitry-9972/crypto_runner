import ccxt
import pandas as pd

from settings import consts


def get_all_currencies_status(exchange):
    print(f"Подключение к {exchange.id} и загрузка данных о валютах...")
    report_data = []
    report_dict = {}

    try:
        # Проверяем, поддерживает ли биржа метод fetch_currencies
        if not hasattr(exchange, 'fetch_currencies'):
            print(f"Ошибка: Биржа {exchange.id} не поддерживает метод fetch_currencies напрямую.")
            print("Попробуем загрузить через load_markets()...")
            exchange.load_markets()
            currencies = exchange.currencies
        else:
            # Запрашиваем актуальный список валют
            currencies = exchange.fetch_currencies()

        if not currencies:
            print("Не удалось получить данные о валютах.")
            return

        print(f"Успешно загружено монет: {len(currencies)}\n")

        # Список для структурирования данных (удобно для вывода или сохранения)


        for code, info in currencies.items():
            # Получаем общие флаги для монеты
            global_deposit = info.get('deposit', 'Unknown')
            global_withdraw = info.get('withdraw', 'Unknown')
            global_status = info.get('status', 'active')

            # Проверяем наличие детальной информации по сетям
            networks = info.get('networks', {})

            if networks:
                # Если сети есть, перебираем каждую
                for net_code, net_info in networks.items():
                    net_deposit = net_info.get('deposit', 'Unknown')
                    net_withdraw = net_info.get('withdraw', 'Unknown')
                    net_active = net_info.get('active', 'Unknown')

                    data_item = {
                        'Token': code,
                        'Global Status': global_status,
                        'Total Deposit': global_deposit,
                        'Total Withdraw': global_withdraw,
                        'Network/Blockchain': net_code,
                        'Network Deposit': net_deposit,
                        'Network Withdraw': net_withdraw,
                        'Network Status': 'Active' if net_active is True else (
                            'Inactive' if net_active is False else 'Unknown')
                    }

                    report_data.append(data_item)

                    if report_dict.get(code):
                        report_dict[code].append(data_item)
                    else:
                        report_dict[code] = [data_item,]
            else:
                # Если биржа не разделяет монету на сети в API
                data_item = {
                    'Token': code,
                    'Global Status': global_status,
                    'Total Deposit': global_deposit,
                    'Total Withdraw': global_withdraw,
                    'Network/Blockchain': 'Default / Single',
                    'Network Deposit': global_deposit,
                    'Network Withdraw': global_withdraw,
                    'Network Status': global_status
                }

                report_data.append(data_item)

                if report_dict.get(code):
                    report_dict[code].append(data_item)
                else:
                    report_dict[code] = [data_item, ]

        # Превращаем в DataFrame для красивого вывода и анализа
        df = pd.DataFrame(report_data)

        # # Выведем первые 50 строк для демонстрации в консоли
        # print(df.to_string(index=False, max_rows=50))

        # Сохраняем результат в CSV файл, чтобы вы могли открыть его в Excel
        filename = f"{exchange.id}_currencies_status.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n Полный отчет успешно сохранен в файл: {filename}")

    except Exception as e:
        print(f"Произошла ошибка при работе с API: {e}")
        raise e

    return report_dict




# print(res)
# print(len(res.keys()))


for exchange_name in consts.EXCHANGES:
    exchange = getattr(ccxt, exchange_name)({
    'options': {
        'fetchCurrencies': True  # Включаем принудительный сбор валют
    }
})
    res = get_all_currencies_status(exchange)
