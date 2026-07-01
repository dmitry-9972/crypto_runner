import datetime
from typing import Dict, Any, List, Tuple
import os

import consts


class IgnoreCache:
    """Класс для кэширования строк игнорирования с временем жизни 1 час"""

    FOREVER_IGNORE_FILE = "ignored_cache_forever.txt"

    def __init__(self):
        self.ignored_lines_cache_list: List[str] = []
        self.ignored_lines_cache_date_list: List[Tuple[str, datetime.datetime]] = []
        self.forever_ignored: set[str] = set()
        self._load_forever_ignored()

    def _load_forever_ignored(self) -> None:
        """Загружает навечно игнорируемые строки из файла"""
        if os.path.exists(self.FOREVER_IGNORE_FILE):
            try:
                with open(self.FOREVER_IGNORE_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped:
                            self.forever_ignored.add(stripped)
            except Exception:
                pass  # silent fail if file issue

    def _save_to_forever(self, cache_key: str) -> None:
        """Сохраняет ключ в файл навечного игнора"""
        try:
            with open(self.FOREVER_IGNORE_FILE, "a", encoding="utf-8") as f:
                f.write(cache_key + "\n")
        except Exception:
            pass  # silent fail

    def get_line_cache(self, line: Dict[str, Any]) -> str:
        """Генерирует уникальный ключ для строки"""
        return (
            f"{line.get('first_exchange_name', '')}"
            f"{line.get('second_exchange_name', '')}"
            f"{line.get('symbol', '')}"
            f"{line.get('spot_futures_comparison', '')}"
            f"{line.get('spot_symbol', '')}"
            f"{line.get('futures_symbol', '')}"
            f"{line.get('spot_exchange_name', '')}"
            f"{line.get('futures_exchange_name', '')}"
        )

    def put(self, line: Dict[str, Any]) -> None:
        """Добавляет строку в кеш игнорирования"""
        cache_key = self.get_line_cache(line)

        if cache_key not in self.ignored_lines_cache_list:
            self.ignored_lines_cache_list.append(cache_key)
            current_time = datetime.datetime.now(datetime.timezone.utc)
            self.ignored_lines_cache_date_list.append((cache_key, current_time))

    def ignore_forever(self, line: Dict[str, Any]) -> None:
        """Добавляет строку в вечный игнор (файл + временный кеш)"""
        cache_key = self.get_line_cache(line)
        if cache_key not in self.forever_ignored:
            self.forever_ignored.add(cache_key)
            self._save_to_forever(cache_key)
        # Также добавляем в обычный кеш
        self.put(line)

    def check(self, line: Dict[str, Any]) -> bool:
        """Проверяет, находится ли строка в игнор-листе и не протухла ли"""
        self._cleanup_expired()  # чистим старые записи

        cache_key = self.get_line_cache(line)

        # Сначала проверяем вечный игнор
        if cache_key in self.forever_ignored:
            return True

        return cache_key in self.ignored_lines_cache_list

    def _cleanup_expired(self) -> None:
        """Удаляет записи старше 1 часа"""
        now = datetime.datetime.now(datetime.timezone.utc)
        one_hour_ago = now - datetime.timedelta(hours=consts.IGNORE_CACHE_EXPIRE_HOURS)

        new_cache_list: List[str] = []
        new_cache_date_list: List[Tuple[str, datetime.datetime]] = []

        for cache_key, timestamp in self.ignored_lines_cache_date_list:
            if timestamp > one_hour_ago:
                new_cache_list.append(cache_key)
                new_cache_date_list.append((cache_key, timestamp))

        self.ignored_lines_cache_list = new_cache_list
        self.ignored_lines_cache_date_list = new_cache_date_list

    def clear(self) -> None:
        """Полная очистка кеша (временного)"""
        self.ignored_lines_cache_list.clear()
        self.ignored_lines_cache_date_list.clear()

    def clear_forever(self) -> None:
        """Очистка вечного игнора (файл + память)"""
        self.forever_ignored.clear()
        if os.path.exists(self.FOREVER_IGNORE_FILE):
            try:
                os.remove(self.FOREVER_IGNORE_FILE)
            except Exception:
                pass

    def get_size(self) -> int:
        """Возвращает текущее количество записей в кеше"""
        return len(self.ignored_lines_cache_list)

    def get_forever_size(self) -> int:
        """Возвращает количество вечных игноров"""
        return len(self.forever_ignored)