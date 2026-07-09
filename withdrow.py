import ccxt
import pandas as pd

# Инициализируем биржу
# Внимание: для получения приватных статусов кошельков некоторым биржам могут потребоваться API-ключи
exchange = ccxt.gate({
    'enableRateLimit': True,
    # 'apiKey': 'YOUR_API_KEY',
    # 'secret': 'YOUR_SECRET_KEY',
})


def get_all_currencies_status():
    print(f"Подключение к {exchange.id} и загрузка данных о валютах...")

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
        report_data = []

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

                    report_data.append({
                        'Токен': code,
                        'Общий статус': global_status,
                        'Депозит (Общий)': global_deposit,
                        'Вывод (Общий)': global_withdraw,
                        'Сеть/Блокчейн': net_code,
                        'Депозит в сети': net_deposit,
                        'Вывод в сети': net_withdraw,
                        'Статус сети': 'Активна' if net_active is True else (
                            'Отключена' if net_active is False else 'Unknown')
                    })
            else:
                # Если биржа не разделяет монету на сети в API
                report_data.append({
                    'Токен': code,
                    'Общий статус': global_status,
                    'Депозит (Общий)': global_deposit,
                    'Вывод (Общий)': global_withdraw,
                    'Сеть/Блокчейн': 'Default / Single',
                    'Депозит в сети': global_deposit,
                    'Вывод в сети': global_withdraw,
                    'Статус сети': global_status
                })

        # Превращаем в DataFrame для красивого вывода и анализа
        df = pd.DataFrame(report_data)

        # Выведем первые 50 строк для демонстрации в консоли
        print(df.to_string(index=False, max_rows=50))

        # Сохраняем результат в CSV файл, чтобы вы могли открыть его в Excel
        filename = f"{exchange.id}_currencies_status.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n Полный отчет успешно сохранен в файл: {filename}")

    except Exception as e:
        print(f"Произошла ошибка при работе с API: {e}")
        raise e



get_all_currencies_status()
