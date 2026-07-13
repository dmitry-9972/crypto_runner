from datetime import datetime, timedelta
import glob
import json
import os
import ccxt

import consts

# Константы настроек
CACHE_PREFIX = "cache_markets"
CACHE_DIR = "cache_markets/"  # Папка для сохранения (текущая)
CACHE_LIFETIME_HOURS = 1


def get_markets_with_cache(exchange: ccxt.Exchange) -> dict:
    """Загружает маркеты биржи с использованием файлового кэша."""
    now = datetime.now()
    valid_cache_found = False
    markets_data = None

    # 1. Ищем существующие файлы кэша для этой биржи
    search_pattern = os.path.join(
        CACHE_DIR, f"{CACHE_PREFIX}_{exchange.id}_*.json"
    )
    cache_files = glob.glob(search_pattern)

    for file_path in cache_files:
        try:
            # Извлекаем дату из имени файла (cache_markets_binance_YYYYMMDD_HHMMSS.json)
            filename = os.path.basename(file_path)
            date_str = filename.replace(
                f"{CACHE_PREFIX}_{exchange.id}_", ""
            ).replace(".json", "")
            file_time = datetime.strptime(date_str, "%Y%m%d_%H%M%S")

            # 2. Проверяем возраст кэша
            if now - file_time < timedelta(hours=CACHE_LIFETIME_HOURS) and not consts.DO_CLEAR_ALL_CACHES:
                print(f"[{exchange.id}] Найдена актуальная копия кэша: {filename}")
                with open(file_path, "r", encoding="utf-8") as f:
                    markets_data = json.load(f)
                valid_cache_found = True
                break
            else:
                # Кэш устарел — удаляем его
                print(f"[{exchange.id}] Удаляем устаревший кэш: {filename}")
                os.remove(file_path)
        except Exception as e:
            print(f"Ошибка при обработке файла кэша {file_path}: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)

    # 3. Если кэш не найден или устарел — делаем запрос к бирже
    if not valid_cache_found:
        print(f"[{exchange.id}] Запрашиваем маркеты через API...")
        # load_markets() возвращает dict, а также сохраняет в exchange.markets
        markets_data = exchange.load_markets()

        # Создаем новое имя файла с текущей датой и временем
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        new_filename = f"{CACHE_PREFIX}_{exchange.id}_{timestamp}.json"
        new_file_path = os.path.join(CACHE_DIR, new_filename)

        # Сохраняем в JSON
        with open(new_file_path, "w", encoding="utf-8") as f:
            json.dump(markets_data, f, ensure_ascii=False, indent=4)
        print(f"[{exchange.id}] Создан новый кэш: {new_filename}")
    else:
        # Если загрузили из кэша, принудительно прокидываем данные в объект exchange
        exchange.markets = markets_data
        exchange.symbols = sorted(list(markets_data.keys()))

    return markets_data


# === ПРИМЕР ИСПОЛЬЗОВАНИЯ ===
if __name__ == "__main__":
    # Инициализируем любую биржу (например, Binance)
    exchange = ccxt.binance({"enableRateLimit": True})

    # Первый запуск — сделает запрос по API и создаст файл
    # Второй запуск (в пределах часа) — прочитает из файла мгновенно
    markets = get_markets_with_cache(exchange)

    # Проверка, что данные на месте
    print(f"Всего загружено рынков: {len(exchange.symbols)}")
    print(f"Пример тикера: {exchange.symbols[0]}")
