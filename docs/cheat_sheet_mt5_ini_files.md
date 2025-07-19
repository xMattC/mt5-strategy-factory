# MetaTrader 5 .ini Configuration Cheat Sheet

## [Tester] Section — General Test Configuration

| Parameter               | Description                                                   | Example                           |
|-------------------------|---------------------------------------------------------------|-----------------------------------|
| `Expert`                | Relative path to the compiled EA (.ex5) under `MQL5\Experts\` | `MyFolder\EA.ex5`                 |
| `Symbol`                | Trading symbol                                                | `EURUSD`                          |
| `Period`                | Chart timeframe                                               | `M1`, `H1`, `Daily`               |
| `Model`                 | Tick generation model                                         | `0=Every tick`, `1=Real ticks`    |
| `UseDate`               | Whether to use a custom date range                            | `true` or `false`                 |
| `FromDate`              | Start date for test (format: `YYYY.MM.DD`)                    | `2015.01.01`                      |
| `ToDate`                | End date for test                                             | `2020.01.01`                      |
| `ForwardMode`           | Forward testing mode                                          | `0=No`, `1=By time`, `2=By ratio` |
| `ForwardDate`           | (Optional) Date to split training/testing                     | `2019.01.01`                      |
| `Deposit`               | Initial deposit                                               | `100000`                          |
| `Currency`              | Deposit currency                                              | `USD`, `EUR`                      |
| `Leverage`              | Account leverage                                              | `100`, `500`                      |
| `ProfitInPips`          | Display profit in pips instead of currency                    | `1=true`, `0=false`               |
| `ExecutionMode`         | Order execution mode                                          | `0=Market`, `1=Instant`           |
| `Optimization`          | Optimization mode                                             | `0=None`, `1=Slow`, `2=Fast`      |
| `OptimizationCriterion` | Optimization target                                           | `0=Balance`, `6=Custom max`, etc. |
| `Visual`                | Run in visual mode (chart visible)                            | `0=no`, `1=yes`                   |
| `ReplaceReport`         | Overwrite existing report file                                | `1=yes`, `0=no`                   |
| `ShutdownTerminal`      | Close MT5 after test                                          | `1=yes`, `0=no`                   |
| `Report`                | Report file name (saved as `.htm`)                            | `TestResults`                     |
| `Journal`               | Optional: path to journal log file                            | `C:\path\log.txt`                 |

## [TesterInputs] Section — EA Parameters and Optimization Ranges

Each input follows this format:

```
param_name = initial||start||step||stop||flag
```

| Segment     | Meaning                                         |
|-------------|-------------------------------------------------|
| `initial`   | The default value used when not optimizing      |
| `start`     | Start value for optimization                    |
| `step`      | Step value for optimization                     |
| `stop`      | Stop value for optimization                     |
| `flag`      | `Y = optimize this input`, `N = keep fixed`     |

### Example:

```
inp_lot_size = 1.0||0.5||0.1||2.0||Y
```

- Start at `0.5`, increment by `0.1`, stop at `2.0`
- Optimize this input because `Y`

```
inp_sl = 20||0||0||0||N
```

- Keep stop loss fixed at `20`, do not optimize

## OptimizationCriterion Values

| Value | Meaning                       |
|-------|-------------------------------|
| 0     | Balance                       |
| 1     | Profit                        |
| 2     | Maximal profit                |
| 3     | Minimal drawdown              |
| 4     | Recovery factor               |
| 5     | Expected payoff               |
| 6     | Custom max (via `OnTester()`) |

## Tips

- **Use `UseDate=true`** or your `FromDate`/`ToDate` will be ignored.
- Set `ShutdownTerminal=1` to close MT5 after the run (good for automation).
- Output reports go to `Tester\Reports`, cache files go to `Tester\cache`.
