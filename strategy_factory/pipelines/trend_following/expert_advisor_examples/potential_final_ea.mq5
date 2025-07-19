#include <MyLibs/BacktestUtils/CustomMax.mqh>
#include <MyLibs/BacktestUtils/TestDataSplit.mqh>
#include <MyLibs/Indicators/AtrBands.mqh>
#include <MyLibs/Indicators/TrendlineAnalyser.mqh>
#include <MyLibs/Orders/AdjustPosition.mqh>
#include <MyLibs/Orders/OrderTracker.mqh>
#include <MyLibs/Orders/EntryOrders.mqh>
#include <MyLibs/Orders/ExitOrders.mqh>
#include <MyLibs/Utils/Enums.mqh>
#include <MyLibs/Utils/MarketDataUtils.mqh>
#include <MyLibs/Utils/MultiSymbolSignalTracker.mqh>
#include <MyLibs/Utils/ResourceManager.mqh>

//--- classes
AdjustPosition adjust_pos;
AtrBands atr_bands;
CustomMax c_max;
OrderTracker order_tracker;
EntryOrders entry_orders;
ExitOrders exit_orders;
MarketDataUtils m_utils;
MultiSymbolSignalTracker track_trigger_signal;
ResourceManager resource_manager;
TestDataSplit data_split;
TrendlineAnalyser tl_tools;

//--- Inputs
//+------------------------------------------------------------------+
//| RISK AND POSITION SETTINGS                                       |
//+------------------------------------------------------------------+
input LOT_MODE inp_lot_mode = LOT_MODE_PCT_RISK;      // Method used for position sizing (e.g., fixed lot, or % risk)
input double inp_lot_var = 2;                         // Lot value or risk percentage (depending on selected lot mode)
input SL_MODE inp_sl_mode = SL_ATR_MULTIPLE;          // Stop Loss method (e.g., ATR-based, fixed value, etc.)
input double inp_sl_var = 1.5;                        // SL parameter (e.g., ATR multiplier or fixed points)
input TP_MODE inp_tp_mode = TP_ATR_MULTIPLE;          // Take Profit method (e.g., ATR-based, fixed value, etc.)
input double inp_tp_var = 1;                          // TP parameter (e.g., ATR multiplier or fixed points)
string lot_mode = EnumToString(inp_lot_mode);         // convert to string
string sl_mode = EnumToString(inp_sl_mode);           // convert to  string
string tp_mode = EnumToString(inp_tp_mode);           // convert to  string
//+------------------------------------------------------------------+
//| BACKTESTING & OPTIMIZATION SETTINGS                              |
//+------------------------------------------------------------------+
input CUSTOM_MAX_TYPE inp_custom_criteria = CM_WIN_PERCENT;    // Custom performance metric to use in OnTester()
input int inp_opt_min_trades = 0;                              // Minimum trades required to validate backtest result
input MODE_SPLIT_DATA inp_data_split_method = NO_SPLIT;        // Method used to split data (e.g., train/test split)
input int inp_force_opt = 1;                                   // Forces optimizer to call OnTester() even if not in training set
//+------------------------------------------------------------------+
//| INDICATOR PERIODS                                                |
//+------------------------------------------------------------------+
input int InpTrendlinePeriod = 100;         // Lookback period for moving average used in trendline
input int InpTriggerPeriod = 14;            // RSI period used to trigger entries
input int InpConformationPeriod = 50;       // CCI period used for confirming trend direction
input int InpExitPeriod = 5;                // Stochastic period used to signal exits

//--- Global vars/arrays
int magic_number = 1000;
int runner_magic = magic_number + 1;
// string SymbolsArray[] = {_Symbol}; // Chart symbol only
string SymbolsArray[] = {"AUDNZD", "EURGBP", "AUDCAD", "CHFJPY", "EURUSD"}; // Multi symbol trading
int tl_handle[], trig_handle[], conf_handle[], vol_handle[], exit_handle[];

int OnInit() {
    ArrayResize(tl_handle, ArraySize(SymbolsArray));
    ArrayResize(trig_handle, ArraySize(SymbolsArray));
    ArrayResize(conf_handle, ArraySize(SymbolsArray));
    ArrayResize(vol_handle, ArraySize(SymbolsArray));
    ArrayResize(exit_handle, ArraySize(SymbolsArray));

    for (int i = 0; i < ArraySize(SymbolsArray); i++) {
        // --- Create and register all indicator handles for this symbol
        tl_handle[i] = iMA(SymbolsArray[i], PERIOD_CURRENT, InpTrendlinePeriod, 0, MODE_SMA, PRICE_CLOSE);
        trig_handle[i] = iRSI(SymbolsArray[i], PERIOD_CURRENT, InpTriggerPeriod, PRICE_CLOSE);
        conf_handle[i] = iCCI(SymbolsArray[i], PERIOD_CURRENT, InpConformationPeriod, PRICE_TYPICAL);
        vol_handle[i] = iOBV(SymbolsArray[i], PERIOD_CURRENT, VOLUME_TICK);
        exit_handle[i] = iStochastic(SymbolsArray[i], PERIOD_CURRENT, InpExitPeriod, 3, 3, MODE_EMA, STO_CLOSECLOSE);
        resource_manager.register_handle(tl_handle[i]);
        resource_manager.register_handle(trig_handle[i]);
        resource_manager.register_handle(conf_handle[i]);
        resource_manager.register_handle(vol_handle[i]);
        resource_manager.register_handle(exit_handle[i]);
    }

    EventSetTimer(60);
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    EventKillTimer();
    resource_manager.release_all_handles();
    track_trigger_signal.clear();
}

double OnTester() {
    return c_max.calculate_custom_criteria(inp_custom_criteria, inp_opt_min_trades);
}

void OnTimer() {
    for (int i = 0; i < ArraySize(SymbolsArray); i++) {
        string symbol = SymbolsArray[i];
        run_trade_logic(symbol, tl_handle[i], trig_handle[i], conf_handle[i], vol_handle[i], exit_handle[i]);
    }
}

void run_trade_logic(string symbol, int tl_hand, int trig_hand, int conf_hand, int vol_hand, int exit_hand) {

    // --- Breakeven logic: if a profit target was reached, move SL to breakeven for runner trades (execution every time step)
    adjust_pos.set_breakeven_if_profit_target_hit(symbol, runner_magic);

    // --- Only run strategy on a new bar to avoid repeated execution within the same candle
    if (!m_utils.is_new_bar(symbol, PERIOD_CURRENT, "00:05")) return;

    // --- ATR-based trailing stop for runner trades only. 
    //      Updated each bar, calculation uses previous bar close. Trail by 1.5x ATR after 2x ATR in profit
    adjust_pos.trailing_stop_atr(symbol, runner_magic, PERIOD_CURRENT, 2.0, 1.5, 14, true);

    // --- Construct signal data structures for long and short directions
    trading_signals long_signals = build_trading_signals(true, symbol, tl_hand, trig_hand, conf_hand, vol_hand, exit_hand);
    trading_signals short_signals = build_trading_signals(false, symbol, tl_hand, trig_hand, conf_hand, vol_hand, exit_hand);

    // --- Determine whether to enter long:
    bool entry_long = 
        standard_entry(long_signals) 
        || pullback_entry(long_signals) 
        || trendline_cross_entry(long_signals);

    // --- Determine whether to enter short:
    bool entry_short = 
        standard_entry(short_signals) 
        || pullback_entry(short_signals) 
        || trendline_cross_entry(short_signals);

    // --- Determine whether exit long:
    bool exit_long = 
        long_signals.exit_indi_sig 
        || long_signals.tl_cross_exit;

    // --- Determine whether exit short:
    bool exit_short = 
        short_signals.exit_indi_sig 
        || short_signals.tl_cross_exit;

    // --- Centralised trade management:
    manage_orders(symbol, entry_long, entry_short, exit_long, exit_short);
}

struct trading_signals {
    bool trigger_sig; int last_trigger_sig; bool trigger_agrees; bool trigger_agrees_prv;   // Trigger signals
    bool conformation;                                                                      // Comformation indicator signal
    bool tl_cross; bool tl_cross_prev; bool tl_agrees; bool tl_agrees_prev;                 // Trendline signals    
    bool atr_b;  bool atr_b_prev; bool atr_pullback;                                        // Atr band signals
    bool volume;                                                                            // Volume indicator signal
    bool exit_indi_sig; bool tl_cross_exit;                                                 // Exit signals
};

trading_signals build_trading_signals(bool is_long, string symbol, int tl_hand, int trig_hand, int conf_hand, int vol_hand, int exit_hand) {

    trading_signals long_sigs;
    trading_signals short_sigs;

    // --- Trigger signals
    bool dummy1 = false, dummy2 = false;
    trigger(trig_hand, long_sigs.trigger_sig, short_sigs.trigger_sig, long_sigs.trigger_agrees, short_sigs.trigger_agrees, 1);
    trigger(trig_hand, dummy1, dummy2, long_sigs.trigger_agrees_prv, short_sigs.trigger_agrees_prv, 2);

    track_trigger_signal.get_tracker(symbol).update_signal_tracker(long_sigs.trigger_sig, short_sigs.trigger_sig);
    long_sigs.last_trigger_sig = track_trigger_signal.get_tracker(symbol).get_long_signal();
    short_sigs.last_trigger_sig = track_trigger_signal.get_tracker(symbol).get_short_signal();

    // --- Trendline crossover and direction signals
    int tl_buffer = 0;
    tl_tools.detect_cross(symbol, tl_hand, tl_buffer, long_sigs.tl_cross, short_sigs.tl_cross, 1);
    tl_tools.detect_cross(symbol, tl_hand, tl_buffer, long_sigs.tl_cross_prev, short_sigs.tl_cross_prev, 2);
    tl_tools.trend_direction(symbol, tl_hand, tl_buffer, long_sigs.tl_agrees, short_sigs.tl_agrees, 1);
    tl_tools.trend_direction(symbol, tl_hand, tl_buffer, long_sigs.tl_agrees_prev, short_sigs.tl_agrees_prev, 2);

        // --- ATR band signals
    // atr_bands.plot_bands(symbol, tl_hand, 14, PERIOD_CURRENT, 1.0, 1); // prit bands (for debugging)
    long_sigs.atr_b = atr_bands.inside_upper_band(symbol, tl_hand, tl_buffer, 14, PERIOD_CURRENT, 1.0, 1);
    short_sigs.atr_b = atr_bands.inside_lower_band(symbol, tl_hand, tl_buffer, 14, PERIOD_CURRENT, 1.0, 1);
    long_sigs.atr_b_prev = atr_bands.inside_upper_band(symbol, tl_hand, tl_buffer, 14, PERIOD_CURRENT, 1.0, 2);
    short_sigs.atr_b_prev = atr_bands.inside_lower_band(symbol, tl_hand, tl_buffer, 14, PERIOD_CURRENT, 1.0, 2);
    long_sigs.atr_pullback = atr_bands.crossed_below_upper_band(symbol, tl_hand, tl_buffer, 14, PERIOD_CURRENT, 1.0, 1);
    short_sigs.atr_pullback = atr_bands.crossed_above_lower_band(symbol, tl_hand, tl_buffer, 14, PERIOD_CURRENT, 1.0, 1);

    // --- Confirmation indicator signals
    conformation(conf_hand, long_sigs.conformation, short_sigs.conformation);

    // --- Volume indicator signals
    volume_filter(vol_hand, long_sigs.volume, short_sigs.volume);


    // --- Exit signals
    exit_signal(exit_hand, long_sigs.exit_indi_sig, short_sigs.exit_indi_sig);
    long_sigs.tl_cross_exit = short_sigs.tl_cross;  // Long exits when price crosses below the trendline
    short_sigs.tl_cross_exit = long_sigs.tl_cross;  // Short exits when price crosses above the trendline

    // --- Return side-specific struct
    return is_long ? long_sigs : short_sigs;
}


// A "standard" entry requires key conditions to be true: trigger, trendline agreement, ATR band position, confirmation, and volume.
// A delayed entry is allowed one bar after the trigger, if confirmation and volume were not ready at the time.
bool standard_entry(const trading_signals& data) {
    bool trigger_sig = data.trigger_sig;                    // Trigger signal occurred on the current candle
    bool trigger_sig_prv = (data.last_trigger_sig == 2);    // Trigger signal occurred on the previous candle
    bool trigger_agrees = data.trigger_agrees;              // Trigger direction still aligns on current candle
    bool tl_agree = data.tl_agrees;                         // Current price is on the correct side of the trendline
    bool tl_agree_prev = data.tl_agrees_prev;               // Previous candle also agreed with trendline direction
    bool inside_atr_band = data.atr_b;                      // Price is within ATR band on current candle
    bool inside_atr_band_prev = data.atr_b_prev;            // Price was within ATR band on previous candle
    bool confirmation = data.conformation;                  // Confirmation indicator aligns with trade direction
    bool volume = data.volume;                              // Volume supports entry

    // --- Standard entry: all conditions met on the current candle
    bool current_entry_valid = trigger_sig && tl_agree && inside_atr_band && confirmation && volume;

    // --- Delayed entry: previous candle had trigger + setup, current candle confirms with vol & confluence
    bool delayed_entry_valid = 
        trigger_sig_prv && tl_agree_prev && inside_atr_band_prev &&  // Previous candle
        trigger_agrees && tl_agree && inside_atr_band && confirmation && volume;        // Current candle
        // this should also have a price pull back filter i.e close is same or lower than last candle close.
    return current_entry_valid || delayed_entry_valid;
}

// A "trendline cross" entry occurs after price crosses the trendline, provided other conditions (ATR band, confirmation, volume)
// are met. Allows 1-bar delay if confirmation and volume were not ready at the time.
bool trendline_cross_entry(const trading_signals& data) {
    bool tl_cross = data.tl_cross;                                          // Trendline cross occurred on current candle **WORKS
    bool tl_cross_prev = data.tl_cross_prev;                                // Trendline cross occurred on previous candle **WORKS
    bool tl_agrees = data.tl_agrees;                                        // Current price is on the correct side of the trendline
    bool trigger_agrees = data.trigger_agrees;                              // Trigger aligns with direction on current candle
    bool trigger_agrees_prev = data.trigger_agrees_prv;                     // Trigger aligned on previous candle
    bool trigger_sig_recent = (data.last_trigger_sig > 0                    // Ensure the signal was actually triggered (not 0 or negative)
                               && data.last_trigger_sig <= 7                // Only consider signals within the last 7 bars
                               && data.last_trigger_sig != EMPTY_VALUE);    // Avoid using uninitialized or invalid values
    bool inside_atr_band = data.atr_b;                                      // Price is inside ATR band on current candle
    bool inside_atr_band_prev = data.atr_b_prev;                            // Price was inside ATR band on previous candle
    bool confirmation = data.conformation;                                  // Confirmation indicator agrees with trade direction
    bool volume = data.volume;                                              // Volume supports entry

    // --- Entry on current candle: trendline cross with trigger agreement, ATR, confirmation and volume
    bool current_entry_valid =
        tl_cross && trigger_agrees && trigger_sig_recent && inside_atr_band && confirmation && volume;

    // --- Delayed entry: trendline cross and alignment happened previously, confirmation and volume caught up now
    bool delayed_entry_valid = 
        tl_cross_prev && trigger_agrees_prev && inside_atr_band_prev &&               // Previous candle
        trigger_sig_recent && trigger_agrees && inside_atr_band && tl_agrees && confirmation && volume;  // Current candle
        // this should also have a price pull back filter i.e close is same or lower than last candle close.

    return current_entry_valid || delayed_entry_valid;
}

// A "Pullback" entry expects price to pull back inside the ATR band 1 bar after a trendline cross.
// The setup must have occurred on the previous candle, and all confirmations must align on the current candle.
bool pullback_entry(const trading_signals& data) {
    bool tl_cross_prev = data.tl_cross_prev;                // Trendline cross occurred on the previous candle
    bool trigger_agrees_prev = data.trigger_agrees_prv;     // Trigger aligned on previous candle
    bool atr_pullback = data.atr_pullback;                  // Price has pulled back into ATR band on current candle
    bool tl_agree = data.tl_agrees;                         // Current price is on the correct side of the trendline
    bool trigger_agrees = data.trigger_agrees;              // Trigger aligns with direction on current candle
    bool confirmation = data.conformation;                  // Confirmation indicator agrees with trade direction
    bool volume = data.volume;                              // Volume supports entry

    // --- Pullback entry: setup on previous candle, pullback + confirmation on current
    return tl_cross_prev && trigger_agrees_prev &&                                // Previous candle
           atr_pullback && tl_agree && trigger_agrees && confirmation && volume;  // Current candle
}

void manage_orders(string symbol, bool long_in, bool short_in, bool exit_long, bool exit_short) {
    // Split risk between TP and runner
    double lot_var = inp_lot_var / 2;

    // --- Always manage open positions regardless of test window ---
    // Close TP positions if exit conditions met
    exit_orders.close_buy_orders(symbol, exit_long, 0, PERIOD_CURRENT, magic_number);
    exit_orders.close_sell_orders(symbol, exit_short, 0, PERIOD_CURRENT, magic_number);

    // Close runner positions if exit triggered
    exit_orders.close_buy_orders(symbol, exit_long, 0, PERIOD_CURRENT, runner_magic);
    exit_orders.close_sell_orders(symbol, exit_short, 0, PERIOD_CURRENT, runner_magic);

    // --- Only open new positions if in test window ---
    if (!data_split.in_test_period(inp_data_split_method)) return;

    // --- Only open new positions if there are no open positions for symbol (regardless of side) ---
    if (order_tracker.count_open_positions(symbol, 0, magic_number) > 0) return;
    if (order_tracker.count_open_positions(symbol, 0, runner_magic) > 0) return;

    // TP entries
    entry_orders.open_buy_orders(symbol, long_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, lot_var, magic_number);
    entry_orders.open_sell_orders(symbol, short_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, lot_var, magic_number);

    // Runner entries
    entry_orders.open_runner_buy_order_with_virtual_tp(symbol, long_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, lot_var, runner_magic);
    entry_orders.open_runner_sell_order_with_virtual_tp(symbol, short_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, lot_var, runner_magic);
}

// Trigger logic
void trigger(int handle, bool& long_sig, bool& short_sig, bool& long_agree, bool& short_agree, int shift = 1) {

    long_sig = false; short_sig = false; long_agree = false; short_agree = false;

    long_sig = false;
    short_sig = false;
    long_agree = false;
    short_agree = false;

    double buffer[];
    ArraySetAsSeries(buffer, true);
    if (CopyBuffer(handle, 0, shift, 2, buffer) <= 0) return;

    long_sig     = (buffer[1] < 50 && buffer[0] > 50);
    short_sig    = (buffer[1] > 50 && buffer[0] < 50);
    long_agree   = (buffer[0] > 50);
    short_agree  = (buffer[0] < 50);
}

// Confirmation logic
void conformation(int handle, bool& long_ok, bool& short_ok) {

    long_ok = false;
    short_ok = false;

    double buffer[];
    ArraySetAsSeries(buffer, true);
    if (CopyBuffer(handle, 0, 1, 1, buffer) <= 0) return;

    long_ok  = (buffer[0] > 0);
    short_ok = (buffer[0] < 0);
}

// Volume filter
void volume_filter(int handle, bool& long_ok, bool& short_ok) {
    long_ok = false;
    short_ok = false;

    double buffer[];
    ArraySetAsSeries(buffer, true);
    if (CopyBuffer(handle, 0, 1, 2, buffer) <= 0) return;

    long_ok  = (buffer[0] > buffer[1]);
    short_ok = (buffer[0] < buffer[1]);
}

// Exit signal
void exit_signal(int handle, bool& exit_long, bool& exit_short) {
    exit_long = false;
    exit_short = false;

    double buffer[];
    ArraySetAsSeries(buffer, true);
    if (CopyBuffer(handle, 0, 1, 2, buffer) <= 0) return;

    exit_long  = (buffer[1] > 50 && buffer[0] < 50);
    exit_short = (buffer[1] < 50 && buffer[0] > 50);
}