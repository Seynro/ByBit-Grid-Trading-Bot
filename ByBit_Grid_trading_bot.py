import ccxt
import time

# Прокси
PROXY = {
    'http': 'proxy_if_needed',
    'https': 'proxy_if_needed',
}

# Bybit API ключи
API_KEY = 'API_KEY'
API_SECRET = 'API_SECRET'


class GridTradingBotBybit:
    def __init__(self, symbol, lower_price, upper_price, grids, investment_amount):
        """
        Инициализация торгового бота.
        :param symbol: Торговая пара (например, 'USDT/USDC').
        :param lower_price: Нижний диапазон сетки.
        :param upper_price: Верхний диапазон сетки.
        :param grids: Количество уровней сетки.
        :param investment_amount: Общая инвестиционная сумма в USDT.
        """
        self.symbol = symbol.replace("/", "")  # Bybit использует пары без символов разделения
        self.lower_price = lower_price
        self.upper_price = upper_price
        self.grids = grids
        self.investment_amount = investment_amount
        self.grid_levels = []
        self.order_size = investment_amount / grids
        self.stop_loss = lower_price * 0.98  # Уровень Stop-Loss
        self.take_profit = upper_price * 1.02  # Уровень Take-Profit

        # Инициализация клиента Bybit через ccxt с прокси
        self.client = ccxt.bybit({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'proxies': PROXY,
            'options': {
                'defaultType': 'spot',  # Указываем работу на спотовом рынке
                'adjustForTimeDifference': True,  # Автоматическая синхронизация времени
            },
        })

    def calculate_grid_levels(self):
        """
        Вычисление уровней сетки с логарифмическим распределением.
        """
        price_step = (self.upper_price / self.lower_price) ** (1 / (self.grids - 1))
        self.grid_levels = [self.lower_price * (price_step ** i) for i in range(self.grids)]
        print("Grid Levels:", self.grid_levels)

    def calculate_atr(self, interval='1h', lookback=14):
        """
        Вычисление Average True Range (ATR) для управления сеткой.
        :param interval: Интервал данных свечей.
        :param lookback: Количество свечей для расчёта ATR.
        """
        ohlcv = self.client.fetch_ohlcv(self.symbol, timeframe=interval, limit=lookback)
        highs = [x[2] for x in ohlcv]
        lows = [x[3] for x in ohlcv]
        atr = sum(high - low for high, low in zip(highs, lows)) / lookback
        return atr

    def calculate_rsi(self, interval='1h', lookback=14):
        """
        Вычисление Relative Strength Index (RSI).
        :param interval: Интервал данных свечей.
        :param lookback: Количество свечей для расчёта RSI.
        """
        ohlcv = self.client.fetch_ohlcv(self.symbol, timeframe=interval, limit=lookback)
        closes = [x[4] for x in ohlcv]
        gains = [closes[i] - closes[i - 1] for i in range(1, len(closes)) if closes[i] > closes[i - 1]]
        losses = [closes[i - 1] - closes[i] for i in range(1, len(closes)) if closes[i] < closes[i - 1]]
        avg_gain = sum(gains) / lookback if gains else 0
        avg_loss = sum(losses) / lookback if losses else 0
        rs = avg_gain / avg_loss if avg_loss > 0 else 0
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def adjust_grid_based_on_volatility(self):
        """
        Динамическое управление сеткой на основе ATR.
        """
        atr = self.calculate_atr()
        print(f"ATR: {atr}")
        price_step = atr / 2  # Шаг сетки в зависимости от ATR
        self.grid_levels = [self.lower_price + i * price_step for i in range(self.grids)]
        print("Adjusted Grid Levels:", self.grid_levels)

    def place_order(self, price, side):
        """
        Размещение лимитного ордера.
        :param price: Цена размещения.
        :param side: 'buy' или 'sell'.
        """
        try:
            order = self.client.create_order(
                symbol=self.symbol,
                type='limit',
                side=side,
                amount=round(self.order_size / price, 5),  # Рассчитать размер ордера
                price=price,
                params={'time_in_force': 'GTC'}  # Good Till Cancelled
            )
            print(f"Order placed: {side} at {price}")
            return order
        except Exception as e:
            print(f"Error placing order: {e}")
            return None



    def setup_grid(self):
        """
        Настройка сетки: покупка ниже текущей цены и продажа выше.
        """
        ticker = self.client.fetch_ticker(self.symbol)
        current_price = ticker['last']
        print(f"Current price: {current_price}")

        for price in self.grid_levels:
            if price < current_price:
                self.place_order(price, 'buy')
            elif price > current_price:
                self.place_order(price, 'sell')

    def monitor_grid(self):
        """
        Мониторинг сетки и управление ордерами.
        """
        print("Monitoring grid...")
        while True:
            try:
                # Получить текущую цену
                ticker = self.client.fetch_ticker(self.symbol)
                current_price = ticker['last']

                # Проверка на срабатывание Stop-Loss или Take-Profit
                if current_price <= self.stop_loss:
                    print(f"Stop-Loss triggered at {current_price}. Exiting.")
                    break
                elif current_price >= self.take_profit:
                    print(f"Take-Profit triggered at {current_price}. Exiting.")
                    break

                # Обновление ордеров
                open_orders = self.client.fetch_open_orders(self.symbol)
                print("Open Orders:", open_orders)
                for order in open_orders:
                    order_price = float(order['price'])
                    if order['status'] == 'closed':
                        self.client.cancel_order(order['id'], self.symbol)
                        if order['side'] == 'buy':
                            print('Placing sell order as buy order closed')
                            self.place_order(order_price * 1.01, 'sell')  # Продать выше
                        elif order['side'] == 'sell':
                            print('Placing buy order as sell order closed')
                            self.place_order(order_price * 0.99, 'buy')  # Купить ниже

                time.sleep(1)  # Частое обновление
            except Exception as e:
                print(f"Error monitoring grid: {e}")
                time.sleep(1)


def main():
    # Параметры бота
    SYMBOL = 'USDE/USDC'
    LOWER_PRICE = 1.0014
    UPPER_PRICE = 1.0021
    GRIDS = 7
    INVESTMENT_AMOUNT = 182  # Общая инвестиция в USDT

    # Инициализация и запуск бота
    bot = GridTradingBotBybit(SYMBOL, LOWER_PRICE, UPPER_PRICE, GRIDS, INVESTMENT_AMOUNT)
    bot.calculate_grid_levels()
    # bot.adjust_grid_based_on_volatility()
    bot.setup_grid()
    bot.monitor_grid()


if __name__ == "__main__":
    main()
