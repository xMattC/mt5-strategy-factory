#include <MyLibs/BacktestUtils/CustomMax.mqh>
#include <MyLibs/BacktestUtils/TestDataSplit.mqh>
#include <MyLibs/Orders/OrderTracker.mqh>
#include <MyLibs/Orders/EntryOrders.mqh>
#include <MyLibs/Orders/ExitOrders.mqh>
#include <MyLibs/Utils/Enums.mqh>
#include <MyLibs/Utils/MarketDataUtils.mqh>
#include <MyLibs/Utils/ResourceManager.mqh>
//--- classes
CustomMax c_max;
OrderTracker order_tracker;
EntryOrders entry_orders;
MarketDataUtils m_utils;
ResourceManager resource_manager;
TestDataSplit data_split;
//--- Inputs
input LOT_MODE inp_lot_mode = LOT_MODE_PCT_RISK;     
input double inp_lot_var = 2;                        
input SL_MODE inp_sl_mode = SL_ATR_MULTIPLE;       
input double inp_sl_var = 1.5;                    
input TP_MODE inp_tp_mode = TP_ATR_MULTIPLE;   
input double inp_tp_var = 1;                    
string lot_mode = EnumToString(inp_lot_mode);    
string sl_mode = EnumToString(inp_sl_mode);   
string tp_mode = EnumToString(inp_tp_mode);  
input CUSTOM_MAX_TYPE inp_custom_criteria = CM_WIN_PERCENT; 
input int inp_opt_min_trades = 0;                           
input MODE_SPLIT_DATA inp_data_split_method = NO_SPLIT;  
input int inp_force_opt = 1;                                  
//+------------------------------------------------------------------+

input int InpConformationPeriod = 14;       

string SymbolsArray[] = {"AUDNZD", "EURGBP", "AUDCAD", "CHFJPY", "EURUSD"}; 

int trig_handle[], conf_handle[];

int OnInit() {
    ArrayResize(trig_handle, ArraySize(SymbolsArray));

    for (int i = 0; i < ArraySize(SymbolsArray); i++) {
        trig_handle[i] = iRSI(SymbolsArray[i], PERIOD_CURRENT, 14, PRICE_CLOSE);
        conf_handle[i] = iCCI(SymbolsArray[i], PERIOD_CURRENT, InpConformationPeriod, PRICE_TYPICAL);

        resource_manager.register_handle(trig_handle[i]);
        resource_manager.register_handle(conf_handle[i]);        
    }

    EventSetTimer(60);
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    EventKillTimer();
    resource_manager.release_all_handles();
}

double OnTester() {
    return c_max.calculate_custom_criteria(inp_custom_criteria, inp_opt_min_trades);
}

void OnTimer() {
    for (int i = 0; i < ArraySize(SymbolsArray); i++) {
        string symbol = SymbolsArray[i];
        run_trade_logic(symbol, trig_handle[i], conf_handle[i]);
    }
}

void run_trade_logic(string symbol, int trig_hand, int conf_hand) {

    if (!m_utils.is_new_bar(symbol, PERIOD_CURRENT, "00:05")) return;

    // --- trigger signal
    bool trigger_long, trigger_short;
    trigger(trig_hand, trigger_long, trigger_short);

    // --- conformation signal
    bool conf_long, conf_short;
    conformation(conf_hand, conf_long, conf_short);

    bool entry_long = 
        trigger_long
        && conf_long;

    bool entry_short = 
        trigger_short
        && conf_short;

    bool exit_long = false;
    bool exit_short = false;

    manage_orders(symbol, entry_long, entry_short, exit_long, exit_short);
}

void manage_orders(string symbol, bool long_in, bool short_in, bool exit_long, bool exit_short) {

    // --- Only open new positions if in test window ---
    if (!data_split.in_test_period(inp_data_split_method)) return;

    // --- Only open new positions if there are no open positions for symbol (regardless of side) ---
    if (order_tracker.count_open_positions(symbol, 0, 1000) > 0) return;

    // TP entries
    entry_orders.open_buy_orders(symbol, long_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, 1000);
    entry_orders.open_sell_orders(symbol, short_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, 1000);
}

void trigger(int handle, bool& long_sig, bool& short_sig) {
    long_sig = false; short_sig = false;

    double buffer[];
    ArraySetAsSeries(buffer, true);
    if (CopyBuffer(handle, 0, 1, 2, buffer) <= 0) return;

    long_sig     = (buffer[1] < 50 && buffer[0] > 50);
    short_sig    = (buffer[1] > 50 && buffer[0] < 50);

}

void conformation(int handle, bool& long_ok, bool& short_ok) {
    long_ok = false; short_ok = false;

    double buffer[];
    ArraySetAsSeries(buffer, true);
    if (CopyBuffer(handle, 0, 1, 1, buffer) <= 0) return;

    long_ok  = (buffer[0] > 0);
    short_ok = (buffer[0] < 0);
}