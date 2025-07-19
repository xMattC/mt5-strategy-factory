# 📄 MQL5 Syntax Cheat Sheet

---

## 🔧 Operators

| Operator | Meaning                      | Example                      |
|----------|------------------------------|------------------------------|
| `=`      | Assignment                   | `x = 5;`                     |
| `==`     | Equal to                     | `if (x == 5)`                |
| `!=`     | Not equal to                 | `if (x != 10)`               |
| `>`      | Greater than                 | `if (price > ma)`            |
| `<`      | Less than                    | `if (price < ma)`            |
| `>=`     | Greater than or equal to     | `if (x >= 100)`              |
| `<=`     | Less than or equal to        | `if (x <= 50)`               |
| `+`      | Addition                     | `a + b`                      |
| `-`      | Subtraction                  | `a - b`                      |
| `*`      | Multiplication               | `a * b`                      |
| `/`      | Division                     | `a / b`                      |
| `%`      | Modulo (remainder)           | `a % 2`                      |
| `&&`     | Logical AND                  | `if (x > 0 && y < 10)`       |
| `||`     | Logical OR                   | `if (x > 0 || y < 10)`       |
| `!`      | Logical NOT                  | `if (!condition)`            |

---

## 🔁 Control Structures

### If / Else
```mql5
if (condition) {
   // do something
} else {
   // do something else
}
```

### For Loop
```mql5
for (int i = 0; i < 10; i++) {
   // repeat 10 times
}
```

### While Loop
```mql5
while (condition) {
   // repeat while condition is true
}
```

### Switch
```mql5
switch (x) {
   case 1: Print("One"); break;
   case 2: Print("Two"); break;
   default: Print("Other");
}
```

---

## 🧩 Data Types

| Type       | Description              | Example                      |
|------------|--------------------------|------------------------------|
| `int`      | Integer                  | `int count = 10;`            |
| `double`   | Decimal / float          | `double price = 1.2345;`     |
| `bool`     | Boolean (true/false)     | `bool signal = true;`        |
| `string`   | Text                     | `string name = "EURUSD";`    |
| `datetime` | Date/time value          | `datetime now = TimeCurrent();` |
| `color`    | Color constant           | `color c = clrBlue;`         |

---

## 📈 Price and Indicator Functions

| Function                      | Description                       |
|-------------------------------|------------------------------------|
| `iClose(symbol, tf, shift)`   | Close price of specified bar      |
| `iOpen(symbol, tf, shift)`    | Open price of specified bar       |
| `iHigh(symbol, tf, shift)`    | High price of specified bar       |
| `iLow(symbol, tf, shift)`     | Low price of specified bar        |
| `iTime(symbol, tf, shift)`    | Time of specified bar             |
| `iMA(...)`                    | Moving average indicator          |

---

## 🧰 Utility Functions

| Function                     | Purpose                             |
|------------------------------|--------------------------------------|
| `Print(...)`                 | Output to Experts log               |
| `Alert(...)`                 | Show popup alert                    |
| `NormalizeDouble(value, d)`  | Round to fixed decimal places       |
| `TimeCurrent()`              | Current server time (datetime)      |

---

## 📦 Arrays

| Function           | Description                     |
|--------------------|---------------------------------|
| `ArraySetAsSeries()` | Make array indexed like a chart (0 = latest bar) |
| `ArraySize()`      | Get number of elements          |
| `ArrayCopy()`      | Copy data from another array    |

---

## 🎨 Colors

| Color Constant     | Example            |
|--------------------|--------------------|
| `clrRed`           | Red color          |
| `clrBlue`          | Blue color         |
| `clrGreen`         | Green color        |
| `clrWhite`, `clrBlack`, `clrYellow`, etc. |

---

## 🔄 Order Constants

| Constant    | Meaning           |
|-------------|-------------------|
| `OP_BUY`    | Buy order         |
| `OP_SELL`   | Sell order        |
| `MODE_SMA`  | Simple MA         |
| `PRICE_CLOSE` | Use close prices |

---

## ✅ Example: MA Cross Strategy

```mql5
double ma = iMA(_Symbol, PERIOD_CURRENT, 14, 0, MODE_SMA, PRICE_CLOSE, 1);
double price = iClose(_Symbol, PERIOD_CURRENT, 1);

if (price > ma) {
   Print("Bullish cross detected.");
}
```
