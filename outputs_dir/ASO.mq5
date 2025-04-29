#include <MyLibs/NNFX_TestFileHeader.mqh>
//-------------------------------------------------------------------------------


input int InpPeriod = 9;

input int InpPeriodSm = 1;

input ENUM_InpMode InpMode = MODE_RSI;

input ENUM_InpMethod InpMethod = MODE_SMA;

input ENUM_InpAppliedPrice InpAppliedPrice = PRICE_CLOSE;


int indicator_handle[];

int OnInit(){
    EventSetTimer(60);

    mf.get_white_list(inp_sym_mode, SymbolsArray);
    ArrayResize(indicator_handle, ArraySize(SymbolsArray));

    for(int i = 0; i < ArraySize(SymbolsArray); i++){
        indicator_handle[i] = iCustom(SymbolsArray[i], PERIOD_CURRENT, "MyIndicators\ASO.ex5", InpPeriod, InpPeriodSm, InpMode, InpMethod, InpAppliedPrice);
    }

    return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason){}

void OnTimer(){
    if(!mf.in_test_period(inp_data_split_method)){return;}
    if(!mf.is_new_bar(_Symbol, PERIOD_CURRENT, "00:05")){return;}

    for(int i = 0; i < ArraySize(SymbolsArray); i++){
        stratagy(SymbolsArray[i], indicator_handle[i]);
    }
}

double OnTester(){
    return cm.calculate_custom_criteria(inp_custom_criteria);
}

void stratagy(string symbol, int indi_handle){
    
    double Bulls[];
    ArraySetAsSeries(Bulls, true);
    CopyBuffer(indi_handle, 0, 1, 10, Bulls);
    
    double Bears[];
    ArraySetAsSeries(Bears, true);
    CopyBuffer(indi_handle, 1, 1, 10, Bears);
    

    bool long_in = (
        Bulls[0] > Bears[0] && Bulls[1] < Bears[1]
    );

    bool short_in = (
        Bulls[0] < Bears[0] && Bulls[1] > Bears[1]
    );

    bool long_out   =   0;
    bool short_out  =   0;

    //--- Manage orders
    om.close_buy_orders(symbol, long_out, 0, PERIOD_CURRENT, 42);
    om.close_sell_orders(symbol, short_out, 0, PERIOD_CURRENT, 42);
    om.open_buy_orders(symbol, long_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, 42);
    om.open_sell_orders(symbol, short_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, 42);
}