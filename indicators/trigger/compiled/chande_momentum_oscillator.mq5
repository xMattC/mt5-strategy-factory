#include <MyLibs/NNFX_TestFileHeader.mqh>

input int CMO_period = 9;
input int CMO_Shift = 0;

int indicator_handle[];  // Handle array for indicators

int OnInit(){
    EventSetTimer(60);
    
    mf.get_white_list(inp_sym_mode, SymbolsArray);
    ArrayResize(indicator_handle, ArraySize(SymbolsArray));
    
    for(int i = 0; i < ArraySize(SymbolsArray); i++){
        indicator_handle[i] = iCustom(SymbolsArray[i], PERIOD_CURRENT, "MyIndicators/chande_momentum_oscillator.ex5", CMO_period, CMO_Shift);
    }
    return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason){}

void OnTimer(){
    if(!mf.in_test_period(inp_data_split_method)){return;}
    
    if(!mf.is_new_bar(_Symbol, PERIOD_CURRENT, "00:05")){return;}
    
    for(int i = 0; i < ArraySize(SymbolsArray); i++){
        strategy(SymbolsArray[i], indicator_handle[i]);
    }
}

double OnTester(){
    return cm.calculate_custom_criteria(inp_custom_criteria);
}

void strategy(string symbol, int trigger_handle){
    bool trigger_long, trigger_short;

    // --- Call modular trigger signal logic
    trigger(trigger_handle, trigger_long, trigger_short);

    bool long_in  = trigger_long;
    bool short_in = trigger_short;
    bool long_out = trigger_short;
    bool short_out = trigger_long;

    //--- Manage orders
    om.close_buy_orders(symbol, long_out, 0, PERIOD_CURRENT, 42);
    om.close_sell_orders(symbol, short_out, 0, PERIOD_CURRENT, 42);
    om.open_buy_orders(symbol, long_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, 42);
    om.open_sell_orders(symbol, short_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, 42);
}

// --- Trigger logic function (add more signal functions as needed)
void trigger(int indi_handle, bool &trigger_long, bool &trigger_short){

    double ExtLineBuffer[];
    ArraySetAsSeries(ExtLineBuffer, true);
    CopyBuffer(indi_handle, 0, 1, 10, ExtLineBuffer);

    trigger_long  = (ExtLineBuffer[0] > 0 && ExtLineBuffer[1] < 0);
    trigger_short = (ExtLineBuffer[0] < 0 && ExtLineBuffer[1] > 0);
}