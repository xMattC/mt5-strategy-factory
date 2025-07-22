#include <MyLibs/BacktestUtils/CustomMax.mqh>
#include <MyLibs/BacktestUtils/TestDataSplit.mqh>
#include <MyLibs/Orders/OrderTracker.mqh>
#include <MyLibs/Orders/EntryOrders.mqh>
#include <MyLibs/Orders/ExitOrders.mqh>
#include <MyLibs/Utils/Enums.mqh>
#include <MyLibs/Utils/MarketDataUtils.mqh>
#include <MyLibs/Utils/ResourceManager.mqh>
#include <MyLibs/Utils/MultiSymbolSignalTracker.mqh>
#include <MyLibs/Indicators/AtrBands.mqh>
#include <MyLibs/Indicators/TrendlineAnalyser.mqh>
//--- classes
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
input LOT_MODE  inp_lot_mode    = LOT_MODE_PCT_RISK;    // Lot Size Mode
input double    inp_lot_var     = 2;                    // Lot Size Var
input SL_MODE   inp_sl_mode     = SL_ATR_MULTIPLE;      // Stop-loss Mode
input double    inp_sl_var      = 1.5;                  // Stop-loss Var
input TP_MODE   inp_tp_mode     = TP_ATR_MULTIPLE;      // Take-profit Mode
input double    inp_tp_var      = 1;                    // Take-Profit Var
string lot_mode = EnumToString(inp_lot_mode);
string sl_mode  = EnumToString(inp_sl_mode);
string tp_mode  = EnumToString(inp_tp_mode);
input CUSTOM_MAX_TYPE inp_custom_criteria = CM_WIN_PERCENT; 
input int inp_opt_min_trades = 0;                           
input MODE_SPLIT_DATA inp_data_split_method = NO_SPLIT;  
input int inp_force_opt = 1;//+------------------------------------------------------------------+
//--- Indicator inputs
//--- Logic inputs
//+------------------------------------------------------------------+
string SymbolsArray[] = { "EURUSD", "AUDNZD", "EURGBP", "AUDCAD", "CHFJPY" };
//+------------------------------------------------------------------+
int trig_handle[], conf_handle[], tl_handle[], volume_handle[];
int magic_number = 1000;

int OnInit() {
    ArrayResize(trig_handle, ArraySize(SymbolsArray));
    ArrayResize(conf_handle, ArraySize(SymbolsArray));
    ArrayResize(tl_handle, ArraySize(SymbolsArray));    
    ArrayResize(volume_handle, ArraySize(SymbolsArray));   
    ArrayResize(exit_handle, ArraySize(SymbolsArray));   
    //---
    for(int i = 0; i < ArraySize(SymbolsArray); i++) {
        trig_handle[i] = iADX(SymbolsArray[i], PERIOD_CURRENT, 14);
        conf_handle[i] = iMACD(SymbolsArray[i], PERIOD_CURRENT, 12, 26, 9, PRICE_CLOSE);
        tl_handle[i] = iMA(SymbolsArray[i], PERIOD_CURRENT, 150, 0, MODE_SMA, PRICE_CLOSE);
        volume_handle[i] = iMFI(SymbolsArray[i], PERIOD_CURRENT, 14, VOLUME_TICK);
        exit_handle[i] = iSAR(SymbolsArray[i], PERIOD_CURRENT, 0.02, 0.2);
        //---
        resource_manager.register_handle(trig_handle[i]);
        resource_manager.register_handle(conf_handle[i]);
        resource_manager.register_handle(tl_handle[i]); 
        resource_manager.register_handle(volume_handle[i]);           
        resource_manager.register_handle(exit_handle[i]);                    
    }
    EventSetTimer(60);
    return(INIT_SUCCEEDED);
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
        run_trade_logic(symbol, trig_handle[i], conf_handle[i], tl_handle[i], volume_handle[i], exit_handle[i]);
    }
}

void run_trade_logic(string symbol, int trig_hand, int conf_hand, int tl_hand, int volume_hand, int exit_hand) {

    if (!m_utils.is_new_bar(symbol, PERIOD_CURRENT, "00:05")) return;

    // --- Construct signal data structures for long and short directions
    trading_signals long_signals = build_trading_signals(true, symbol, tl_hand, trig_hand, conf_hand, volume_hand, exit_hand);
    trading_signals short_signals = build_trading_signals(false, symbol, tl_hand, trig_hand, conf_hand, volume_hand, exit_hand);

    // --- Determine whether to enter long:
    bool entry_long = standard_entry(long_signals) || trendline_cross_entry(long_signals);

    // --- Determine whether to enter short:
    bool entry_short = standard_entry(short_signals) || trendline_cross_entry(short_signals);

    // --- Determine whether exit long:
    bool exit_long = long_signals.tl_cross_exit || long_signals.exit_indi_sig;

    // --- Determine whether exit short:
    bool exit_short = short_signals.tl_cross_exit || short_signals.exit_indi_sig;

    // --- trade management:
    manage_orders(symbol, entry_long, entry_short, exit_long, exit_short);
}

struct trading_signals {
    bool trigger_sig;     
    bool last_trigger_sig;
    bool trigger_agrees;
    bool conformation;      
    bool tl_cross;
    bool trend_direction; 
    bool inside_atr_band; 
    bool volume;   
    bool exit_indi_sig;      
    bool tl_cross_exit; 
};

trading_signals build_trading_signals(bool is_long, string symbol, int tl_hand, int trig_hand, int conf_hand, int volume_hand, int exit_hand) {

    trading_signals long_signals;
    trading_signals short_sigsnals;

    // Trigger Signals
    trigger(trig_hand, long_signals.trigger_sig, short_sigsnals.trigger_sig, long_signals.trigger_agrees, short_sigsnals.trigger_agrees);
    track_trigger_signal.get_tracker(symbol).update_signal_tracker(long_signals.trigger_sig, short_sigsnals.trigger_sig);

    // Conformation Signals
    conformation(conf_hand, long_signals.conformation, short_sigsnals.conformation);

    // volume Signals
    volume(volume_hand, long_signals.volume, short_sigsnals.volume);

    // Trendline Signals
    int tl_buffer = 0;
    tl_tools.detect_cross(symbol, tl_hand, 0, long_signals.tl_cross, short_sigsnals.tl_cross, 1);
    tl_tools.trend_direction(symbol, tl_hand, 0, long_signals.trend_direction, short_sigsnals.trend_direction, 1);

    // ATR Bands Signals
    long_signals.inside_atr_band = atr_bands.inside_upper_band(symbol, tl_hand, tl_buffer, 14, PERIOD_CURRENT, 1.0, 1);
    short_sigsnals.inside_atr_band = atr_bands.inside_lower_band(symbol, tl_hand, tl_buffer, 14, PERIOD_CURRENT, 1.0, 1);
    // atr_bands.plot_bands(symbol, tl_hand, 14, PERIOD_CURRENT, 1.0, 1); // prit bands (for debugging)

    // Exit Signals
    exit_signal(exit_hand, long_signals.exit_indi_sig, short_sigsnals.exit_indi_sig);
    long_signals.tl_cross_exit = short_sigsnals.tl_cross;  // Long exits when price crosses below the trendline
    short_sigsnals.tl_cross_exit = long_signals.tl_cross;  // Short exits when price crosses above the trendline

    return is_long ? long_signals : short_sigsnals;
}

bool standard_entry(const trading_signals& data) {
    bool trigger_sig = data.trigger_sig;            // Trigger signal occurred on the current candle
    bool trend_direction = data.trend_direction;    // Current price is on the correct side of the trendline
    bool inside_atr_band = data.inside_atr_band;    // Price is inside ATR band
    bool confirmation = data.conformation;          // Confirmation indicator aligns with trade direction
    bool volume = data.volume;                      // Volume indicator aligns with trade direction

    return trigger_sig && trend_direction && inside_atr_band && confirmation && volume;
}

bool trendline_cross_entry(const trading_signals& data) {
    bool tl_cross = data.tl_cross;                  // Trendline cross occurred on current candle
    bool trigger_agrees = data.trigger_agrees;      // Trigger aligns with trend direction
    bool inside_atr_band = data.inside_atr_band;    // Price is inside ATR band
    bool confirmation = data.conformation;          // Confirmation indicator agrees
    bool volume = data.volume;                      // Volume indicator agrees

    bool trigger_sig_recent = (data.last_trigger_sig <= 7   // Trigger signal occured within the last 7 bars
                               &&data.last_trigger_sig > 0  // Ensure the signal was actually triggered (not 0 or negative)
                               && data.last_trigger_sig != EMPTY_VALUE);  // Avoid using uninitialized or invalid values

    return tl_cross && trigger_agrees && trigger_sig_recent && inside_atr_band && confirmation && volume;
}

void manage_orders(string symbol, bool long_in, bool short_in, bool exit_long, bool exit_short) {
    
    // Exits 
    exit_orders.close_buy_orders(symbol, exit_long, 0, PERIOD_CURRENT, magic_number);
    exit_orders.close_sell_orders(symbol, exit_short, 0, PERIOD_CURRENT, magic_number);

    // Entries
    if (!data_split.in_test_period(inp_data_split_method)) return;
    if (order_tracker.count_open_positions(symbol, 0, magic_number) > 0) return;  // No hedging!
    entry_orders.open_buy_orders(symbol, long_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, magic_number);
    entry_orders.open_sell_orders(symbol, short_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, magic_number);
}

void trigger(int handle, bool& long_sig, bool& short_sig, bool& long_agree, bool& short_agree, int shift = 1) {

    long_sig = false; short_sig = false; long_agree = false; short_agree = false;
    
    double PlusDI[];
    ArraySetAsSeries(PlusDI, true);
    CopyBuffer(handle, 1, 1, 10, PlusDI);
    
    double MinusDI[];
    ArraySetAsSeries(MinusDI, true);
    CopyBuffer(handle, 2, 1, 10, MinusDI);
    
    long_sig = (PlusDI[0] > MinusDI[0] && PlusDI[1] < MinusDI[1]);
    short_sig = (PlusDI[0] < MinusDI[0] && PlusDI[1] > MinusDI[1]);
    long_agree = (PlusDI[0] > MinusDI[0]);
    short_agree = (PlusDI[0] < MinusDI[0]);
}

void conformation(int handle, bool& long_ok, bool& short_ok) {

    long_ok = false; short_ok = false;
    
    double MACD[];
    ArraySetAsSeries(MACD, true);
    CopyBuffer(handle, 0, 1, 10, MACD);
    
    double Signal[];
    ArraySetAsSeries(Signal, true);
    CopyBuffer(handle, 1, 1, 10, Signal);
    
    long_ok = (MACD[0] > Signal[0]);
    short_ok = (MACD[0] < Signal[0]);
}

void volume(int handle, bool& long_ok, bool& short_ok) {
    long_ok = false; short_ok = false;
    
    double MFI[];
    ArraySetAsSeries(MFI, true);
    CopyBuffer(handle, 0, 1, 10, MFI);
    
    long_ok = (MFI[0] > 50);
    short_ok = (MFI[0] < 50);
}

void exit_signal(int handle, bool& exit_long, bool& exit_short) {
    exit_long = false; exit_short = false;
    
    double SAR[];
    ArraySetAsSeries(SAR, true);
    CopyBuffer(handle, 0, 1, 10, SAR);
    
    exit_long = (close[0] < SAR[0] && close[1] > SAR[1]);
    exit_short = (close[0] > SAR[0] && close[1] < SAR[1]);
}