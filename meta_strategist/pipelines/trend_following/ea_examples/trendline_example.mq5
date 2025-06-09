#include <MyLibs/Myfunctions.mqh>
#include <MyLibs/OrderManagement.mqh>
#include <MyLibs/MyEnums.mqh>
#include <MyLibs/CustomMax.mqh>
CustomMax cm;
MyFunctions mf;
OrderManagment om;
//---
input LOT_MODE  inp_lot_mode    = LOT_MODE_PCT_RISK;    // Lot Size Mode
input double    inp_lot_var     = 2;                    // Lot Size Var
input SL_MODE   inp_sl_mode     = SL_ATR_MULTIPLE;      // Stop-loss Mode
input double    inp_sl_var      = 1.5;                    // Stop-loss Var
input TP_MODE   inp_tp_mode     = TP_ATR_MULTIPLE;      // Take-profit Mode
input double    inp_tp_var      = 1;                  // Take-Profit Var
string lot_mode = EnumToString(inp_lot_mode);
string sl_mode  = EnumToString(inp_sl_mode);
string tp_mode  = EnumToString(inp_tp_mode);
input CUSTOM_MAX_TYPE inp_custom_criteria = CM_WIN_PERCENT;
input int inp_opt_min_trades = 0; // 0/off
input MODE_SPLIT_DATA inp_data_split_method = NO_SPLIT;
input int inp_force_opt = 1;
input group "-----------------------------------------"




input int inp_rsi_period = 14;

input int applied_price = PRICE_CLOSE;


string SymbolsArray[] = { "EURUSD", "AUDNZD", "EURGBP", "AUDCAD", "CHFJPY" };

int trigger_handle[];   // Handles for trigger indicators
int conf_handle[];      // Handles for conformation indicators

int OnInit(){
    EventSetTimer(60);

    ArrayResize(trigger_handle, ArraySize(SymbolsArray));
    ArrayResize(conf_handle, ArraySize(SymbolsArray));

    for(int i = 0; i < ArraySize(SymbolsArray); i++){
    
        trigger_handle[i] = iADX(SymbolsArray[i], PERIOD_CURRENT, 37);
    
    
        conf_handle[i] = iRSI(SymbolsArray[i], PERIOD_CURRENT, inp_rsi_period, applied_price);
    
    }
    return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason){}

void OnTimer(){

    if(!mf.in_test_period(inp_data_split_method)){return;}

    if(!mf.is_new_bar(_Symbol, PERIOD_CURRENT, "00:05")){return;}

    for(int i = 0; i < ArraySize(SymbolsArray); i++){
        strategy(SymbolsArray[i], trigger_handle[i], conf_handle[i]);
    }
}

double OnTester(){
    return cm.calculate_custom_criteria(inp_custom_criteria, inp_opt_min_trades);
}

// Main logic function
void strategy(string symbol, int trigger_hand, int conf_hand){

    bool trigger_long, trigger_short;
    trigger(trigger_hand, trigger_long, trigger_short);

    bool conf_long, conf_short;
    conformation(conf_hand, conf_long, conf_short);

    bool long_in = (trigger_long
                    && conf_long);

    bool short_in = (trigger_short
                     && conf_short);

    bool long_out = 0;
    bool short_out = 0;

    //--- Manage orders
    om.close_buy_orders(symbol, long_out, 0, PERIOD_CURRENT, 42);
    om.close_sell_orders(symbol, short_out, 0, PERIOD_CURRENT, 42);
    om.open_buy_orders(symbol, long_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, 42);
    om.open_sell_orders(symbol, short_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, 42);
}

// Conformation logic (from indicator YAML)
void conformation(int indi_handle, bool &conf_long, bool &conf_short){

    
    double RSI[];
    ArraySetAsSeries(RSI, true);
    CopyBuffer(indi_handle, 0, 1, 10, RSI);

    
    conf_long = (RSI[0] > 50);
    conf_short = (RSI[0] < 50);
}

// Trigger logic (from IS-optimised trigger YAML/result)
void trigger(int indi_handle, bool &trigger_long, bool &trigger_short){

    
    double Main[];
    ArraySetAsSeries(Main, true);
    CopyBuffer(indi_handle, 0, 1, 10, Main);

    
    double PlusDI[];
    ArraySetAsSeries(PlusDI, true);
    CopyBuffer(indi_handle, 1, 1, 10, PlusDI);

    
    double MinusDI[];
    ArraySetAsSeries(MinusDI, true);
    CopyBuffer(indi_handle, 2, 1, 10, MinusDI);

    
    trigger_long = (PlusDI[0] > MinusDI[0]);
    trigger_short = (PlusDI[0] < MinusDI[0]);
}