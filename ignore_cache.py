import datetime
from typing import Dict, Any, List, Tuple

import consts


class IgnoreCache:
    """Класс для кэширования строк игнорирования с временем жизни 1 час"""

    def __init__(self):
        self.ignored_lines_cache_list: List[str] = []
        self.ignored_lines_cache_date_list: List[Tuple[str, datetime.datetime]] = []

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

    def check(self, line: Dict[str, Any]) -> bool:
        """Проверяет, находится ли строка в игнор-листе и не протухла ли"""
        self._cleanup_expired()  # чистим старые записи

        cache_key = self.get_line_cache(line)
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
        """Полная очистка кеша"""
        self.ignored_lines_cache_list.clear()
        self.ignored_lines_cache_date_list.clear()

    def get_size(self) -> int:
        """Возвращает текущее количество записей в кеше"""
        return len(self.ignored_lines_cache_list)


