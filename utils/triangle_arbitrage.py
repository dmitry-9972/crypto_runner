import math
from collections import defaultdict
from typing import Dict, List, Tuple

from comparer import Comparer

from collections import defaultdict
from typing import Dict, List, Tuple


class TradeStep:
    def __init__(self, from_curr: str, to_curr: str, exchange: str, multiplier: float):
        self.from_curr = from_curr
        self.to_curr = to_curr
        self.exchange = exchange
        self.multiplier = multiplier


class ArbitrageOpportunity:
    def __init__(self, steps: List[TradeStep], profit: float, start_amount: float = 1000.0):
        self.steps = steps
        self.profit = profit
        self.start_amount = start_amount
        self.final_amount = start_amount * profit

    def __str__(self):
        lines = []
        prev = None
        for s in self.steps:
            lines.append(f"{s.from_curr} → {s.to_curr} ({s.exchange})")
        path_str = "\n   ".join(lines)
        return (f"АРБИТРАЖ (прибыль {self.profit:.4f}x | +{(self.profit - 1) * 100:.2f}%)\n"
                f"   {path_str}\n"
                f"{self.start_amount:.2f} USDT → {self.final_amount:.2f} USDT")


def build_graph_with_exchanges(client1, client2, name1="Binance", name2="Bybit"):
    graph = defaultdict(list)
    for client, ex_name in [(client1, name1), (client2, name2)]:
        for symbol, price in getattr(client, 'spot_current_prices', {}).items():
            if price <= 0:
                continue
            try:
                base, quote = symbol.split('/') if '/' in symbol else (symbol, "USDT")
                base, quote = base.strip(), quote.strip()

                # quote -> base
                graph[quote].append((base, ex_name, 1.0 / price))
                # base -> quote
                graph[base].append((quote, ex_name, float(price)))
            except:
                continue
    return graph


def find_arbitrage_opportunities(
        graph, max_depth=6, min_profit=1.001, stablecoin="USDT"
):
    opportunities = []

    def dfs(current, path_steps: List[TradeStep], product, depth):
        if depth > max_depth:
            return

        for to_curr, ex, mult in graph[current]:
            if mult <= 0:
                continue

            new_step = TradeStep(current, to_curr, ex, mult)
            new_product = product * mult
            new_path = path_steps + [new_step]

            # Цикл обратно в USDT
            if to_curr == stablecoin and len(new_path) >= 3 and new_product >= min_profit:
                opportunities.append(ArbitrageOpportunity(new_path, new_product))
                continue

            # Проверка на зацикливание (кроме финального возврата)
            if any(step.to_curr == to_curr for step in path_steps) and to_curr != stablecoin:
                continue

            dfs(to_curr, new_path, new_product, depth + 1)

    print("Поиск цепочек USDT → ... → USDT ...")
    # Запускаем строго от USDT
    dfs(stablecoin, [], 1.0, 1)

    # Сортируем по прибыли
    opportunities.sort(key=lambda x: x.profit, reverse=True)

    # Убираем дубликаты
    unique = []
    seen = set()
    for opp in opportunities:
        key = tuple((s.from_curr, s.to_curr, s.exchange) for s in opp.steps)
        if key not in seen:
            seen.add(key)
            unique.append(opp)

    return unique


def find_cross_exchange_arbitrage(client1, client2,
                                  name1: str = "Binance",
                                  name2: str = "Bybit",
                                  max_depth: int = 6,
                                  min_profit: float = 1.001):
    print("=== Поиск арбитража (USDT → ... → USDT) ===\n")
    graph = build_graph_with_exchanges(client1, client2, name1, name2)

    print(f"Валют: {len(graph)} | Направлений: {sum(len(v) for v in graph.values())}\n")

    opportunities = find_arbitrage_opportunities(
        graph, max_depth=max_depth, min_profit=min_profit
    )

    if not opportunities:
        print("Возможностей не найдено.")
        return

    print(f"Найдено {len(opportunities)} возможностей:\n")
    for i, opp in enumerate(opportunities[:15], 1):
        print(f"{i:2d}. {opp}")
        print("-" * 85)


comparer = Comparer()
comparer.refresh_all_exchanges_and_prices()




find_cross_exchange_arbitrage(
    comparer.all_exchanges[0],
    comparer.all_exchanges[1],
    name1=comparer.all_exchanges[0].exchange_name,
    name2=comparer.all_exchanges[1].exchange_name,
    max_depth=3,
    min_profit=1.001
)