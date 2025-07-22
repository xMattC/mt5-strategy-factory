# Trend Following System Outline

This trading system is a fully rule-based, algorithmic approach to trend-following in the forex market. It's built specifically for the **daily (D1) timeframe**, with the aim of removing discretionary decision-making entirely. Rather than relying on chart patterns or subjective analysis, it uses a structured pipeline of indicators, each with a defined purpose, to identify, filter, and manage trades.

## Core Components

### 1. Trend Line
**Purpose:** Establishes directional bias and filters trades accordingly.  
**Logic:** Only long trades are allowed when price is above the trend line, and only shorts when price is below.

**Examples:**
- Hull Moving Average (HMA)
- Double Exponential Moving Average (DEMA)
- Kaufman's Adaptive Moving Average (KAMA)
- Weighted Moving Average (WMA)

---

### 2. Trigger  
**Purpose:** Acts as the primary entry signal generator, identifying momentum aligned with the trend.  
**Logic:** Signals must be in the direction of the trend line. Valid triggers might be based on crossovers, histogram shifts, or level breaks.

**Examples:**
- SSL Channel
- CCI
- DMI/ADX Cross
- MACD Histogram
- Custom oscillators

---

### 3. Confirmation  
**Purpose:** Provides additional confirmation to validate trigger signals and reduce false positives.  
**Logic:** Measures trend strength or momentum to support the trigger's direction.

**Examples:**
- Relative Vigor Index (RVI)
- ADX
- Momentum
- RSI

---

### 4. Volume Filter  
**Purpose:** Screens for sufficient market activity before entering a trade.  
**Logic:** Filters out trades during thin or low-volume periods (e.g., post-Asia session, holidays).

**Examples:**
- Money Flow Index (MFI)
- Volume-Weighted MACD
- Custom tick volume indicators

---

### 5. Exit Indicator  
**Purpose:** Provides discretionary-style exits via objective logic when price fails to reach TP or SL.  
**Logic:** Closes the trade if a trend reversal or exhaustion is signalled.

**Examples:**
- ATR Trailing Stop
- QQE
- Opposite Trigger signal

---

## Entry Conditions

A trade is only taken when **all** of the following are true:

1. Price is on the correct side of the **trend line**.
2. A valid **trigger** appears in the direction of the trend.
3. The **confirmation** indicator agrees with the trigger.
4. The **volume filter** confirms that conditions are tradable.

This strict confluence ensures the system avoids weak or conflicting signals and only enters during optimal conditions.

---

## Exits

### Take Profit (TP)
- A fixed ATR multiple is used (e.g. 1.5× ATR).
- A portion of the position may be closed at TP, while the rest is left to run with a trailing stop.

### Stop Loss (SL)
- Placed based on ATR (e.g. 1.5× ATR).
- Can be adjusted to breakeven or trailed after 1R is reached.

### Exit Indicator
- If the exit indicator signals against the trade, the position is closed immediately — regardless of TP/SL.

---

## Position Sizing

Position sizing is calculated based on risk per trade:

- The stop distance is determined using ATR.
- The lot size is calculated to risk a fixed % of account equity (typically 1%).
- This maintains consistent risk exposure across trades, regardless of volatility.

---

## General Concepts

- **Backtesting:**  
  Every component should be independently tested on both in-sample and out-of-sample data. This helps ensure each part of the system is robust and not overfit to historical price action.

- **Walk-Forward Thinking:**  
  Components must be designed and tested as if operating in real time. That means no future peeking and no indicators that repaint.

- **Strict Rule-Based Logic:**  
  No trades are taken unless every condition is satisfied. This removes emotional influence and creates consistent execution.

- **One Trade per Pair Rule:**  
  To limit exposure and avoid correlation risk, only one open position is allowed per currency pair at any time. 
  (i.e, trading USD/GBP and USD/EUR at same time would not be allowed)

- **Consistent Risk Management:**  
  All trades adhere to a fixed risk-per-trade model (usually 1%). Risk does not increase based on “confidence” in a setup.

- **Indicator Independence:**  
  Each indicator in the pipeline should measure something distinct. For example, don’t use two momentum indicators in both the trigger and confirmation slots.

- **Data Hygiene:**  
  Always verify the accuracy of your historical data during backtesting. Bad feeds or gaps can produce misleading results.

---

This framework is designed for clean integration into automated strategies or system development pipelines. It's systematic, scalable, and adaptable to other instruments with appropriate modifications.
