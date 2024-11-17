## **Bybit Grid Trading Bot**

A fully automated **grid trading bot** for the Bybit spot market, built using Python and the `ccxt` library. This bot is designed to help traders execute a grid trading strategy, which involves buying low and selling high within a predefined price range, maximizing profits in a sideways or slightly volatile market.

---

### **Features**

- **Grid Trading Strategy**: Automatically creates buy and sell orders at multiple price levels within a specified range.
- **ATR-Based Adjustments**: (Optional) Dynamically adjusts grid levels based on Average True Range (ATR) to account for market volatility.
- **RSI Analysis**: (Optional) Includes Relative Strength Index (RSI) calculation for market analysis and informed decision-making.
- **Stop-Loss and Take-Profit**: Protect your capital with predefined Stop-Loss and Take-Profit levels.
- **Real-Time Market Monitoring**: Continuously tracks price movements and manages open orders.
- **Proxy Support**: Easily integrates proxy for secure and private trading.

---

### **How It Works**

1. **Define Parameters**: Set the trading pair, price range, number of grid levels, and total investment amount.
2. **Grid Levels Calculation**: The bot calculates price levels within the specified range for placing buy and sell orders.
3. **Order Placement**: Creates buy orders below the current price and sell orders above it.
4. **Monitoring and Adjustment**:
   - Monitors the market in real time to execute and replace orders dynamically.
   - If a buy order is executed, a corresponding sell order is created at a higher price (and vice versa).
5. **Profit Protection**: Stops trading when the price hits Stop-Loss or Take-Profit thresholds.

---

### **Prerequisites**

- Python 3.8 or higher
- A Bybit account with an API key and secret
- Install required libraries:
  ```bash
  pip install ccxt
  ```

---

### **Installation and Usage**

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bybit-grid-bot.git
   cd bybit-grid-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure API keys and parameters in the script:
   - Replace `API_KEY` and `API_SECRET` with your Bybit API credentials.
   - Define the trading pair, price range, grid levels, and investment amount.

4. Run the bot:
   ```bash
   python bot.py
   ```

---

### **Example Configuration**

```python
SYMBOL = 'USDC/USDT'         # Trading pair
LOWER_PRICE = 0.999          # Lower price range
UPPER_PRICE = 1.001          # Upper price range
GRIDS = 7                    # Number of grid levels
INVESTMENT_AMOUNT = 100      # Total investment in USDT
```

---

### **Disclaimer**

This bot is provided as-is for educational purposes only. Use it at your own risk. The author is not responsible for any financial losses incurred while using this bot. Always test with small amounts or on a demo account before deploying it with significant capital.

---

### **Contributions**

Contributions are welcome! Feel free to fork the repository, submit issues, or create pull requests for enhancements or bug fixes.

---

### **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### **Future Improvements**

- Enhance grid adjustment logic with AI/ML insights.
