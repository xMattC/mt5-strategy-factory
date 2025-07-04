#include <MyLibs/Strategy/EntryLogic_nnfx.mqh>
#include <MyLibs/Utils/MarketDataUtils.mqh>
#include <MyLibs/Utils/Enums.mqh>
#include <MyLibs/BacktestUtils/CustomMax.mqh>
#include <MyLibs/BacktestUtils/TestDataSplit.mqh>
#include <MyLibs/Orders/EntryOrders.mqh>
#include <MyLibs/Orders/ExitOrders.mqh>
//--- 
CustomMax c_max;
TestDataSplit data_split;
MarketDataUtils mdu;
EntryOrders entry_orders;
ExitOrders exit_orders;
EntryState entry_state;
EntryLogic entry_logic;
//---
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
input int inp_opt_min_trades = 0; // 0/off
input MODE_SPLIT_DATA inp_data_split_method = NO_SPLIT;
input int inp_force_opt = 1;
input group "-----------------------------------------"
input int InpBaselinePeriod = 50;
//---
string SymbolsArray[] = { "EURUSD", "AUDNZD", "EURGBP", "AUDCAD", "CHFJPY" };
//---
int baseline_handle[], atr_handle[], trig_handle[], conf_handle[], vol_handle[], exit_handle[];

int OnInit(){

   ArrayResize(baseline_handle, ArraySize(SymbolsArray));
   ArrayResize(atr_handle, ArraySize(SymbolsArray));
   ArrayResize(trig_handle, ArraySize(SymbolsArray));
   ArrayResize(conf_handle, ArraySize(SymbolsArray));
   ArrayResize(vol_handle, ArraySize(SymbolsArray));
   ArrayResize(exit_handle, ArraySize(SymbolsArray));

   for(int i = 0; i < ArraySize(SymbolsArray); i++){
      baseline_handle[i] = iMA(SymbolsArray[i], PERIOD_CURRENT, InpBaselinePeriod, 0, MODE_SMA, PRICE_CLOSE);
      atr_handle[i] = iATR(SymbolsArray[i], PERIOD_CURRENT, 14);
      trig_handle[i] = iRSI(SymbolsArray[i], PERIOD_CURRENT, 14, PRICE_CLOSE);
      conf_handle[i] = iRSI(SymbolsArray[i], PERIOD_CURRENT, 14, PRICE_CLOSE);
      vol_handle[i] = iRSI(SymbolsArray[i], PERIOD_CURRENT, 14, PRICE_CLOSE);
      exit_handle[i] = iRSI(SymbolsArray[i], PERIOD_CURRENT, 14, PRICE_CLOSE);      
   }

   EventSetTimer(60);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason){
    EventKillTimer();
}

double OnTester(){
    return c_max.calculate_custom_criteria(inp_custom_criteria, inp_opt_min_trades);
}

void OnTimer() {

    if(!data_split.in_test_period(inp_data_split_method)){return;}

    if(!mdu.is_new_bar(_Symbol, PERIOD_CURRENT, "00:05")){return;}

    for(int i = 0; i < ArraySize(SymbolsArray); i++){
        strategy(SymbolsArray[i], baseline_handle[i], atr_handle[i], trig_handle[i], conf_handle[i], vol_handle[i], exit_handle[i]);
    }
}

void strategy(string symbol, int baseline_hand, int atr_hand,int trig_hand, int conf_hand, int vol_hand, int exit_hand){

    int curr_bar = iBars(symbol, PERIOD_CURRENT) - 1;
    double price = iClose(symbol, PERIOD_CURRENT, 0);
    double prev_price = iClose(symbol, PERIOD_CURRENT, 1);
    double baseline = mdu.get_latest_buffer_value(baseline_hand);
    double prev_baseline = mdu.get_buffer_value(baseline_hand, 1);
    double atr = mdu.get_latest_buffer_value(atr_hand);

    // Entry trigger signal
    bool trig_long, trig_short;
    trigger(trig_hand, trig_long, trig_short);

    // Confirmation indicator 
    bool conf_long, conf_short;
    conformation(conf_hand, conf_long, conf_short);

    // Volume condition
    bool vol_long, vol_short;
    volume_filter(vol_hand, vol_long, vol_short);
      
    // Exit condition
    bool exit_long, exit_short;
    exit_signal(exit_hand, exit_long, exit_short);  

    // Track last trigger and trend cross events
    entry_state.update_trigger(trig_long, trig_short, curr_bar);
    entry_state.update_baseline_cross(curr_bar, price, baseline, prev_price, prev_baseline);

    // Check if signal is recent (e.g., within 7 candles)
    bool recent_trigg_long = is_recent(entry_state.get_last_trigger(true), curr_bar, 7);
    bool recent_trigg_short = is_recent(entry_state.get_last_trigger(false), curr_bar, 7);

    // Build context to simplify long/short evaluations
    EntryContext long_ctx = build_entry_context(true, price, baseline, atr, entry_state.get_last_cross(true), entry_state.get_last_entry(true), trig_long, conf_long, vol_long, recent_trigg_long);
    EntryContext short_ctx = build_entry_context(false, price, baseline, atr, entry_state.get_last_cross(false), entry_state.get_last_entry(false), trig_short, conf_short, vol_short, recent_trigg_short);

    // Entry rule entry_logic: multiple methods allowed
    bool long_in = entry_logic.is_standard_entry(long_ctx);
                // || entry_logic.is_pullback_entry(long_ctx, curr_bar)
                // || entry_logic.is_baseline_cross_entry(long_ctx, prev_price, prev_baseline, price, baseline, true)
                // || entry_logic.is_continuation_entry(long_ctx, curr_bar, 10);

    bool short_in = entry_logic.is_standard_entry(short_ctx);
                // || entry_logic.is_pullback_entry(short_ctx, curr_bar)
                // || entry_logic.is_baseline_cross_entry(short_ctx, prev_price, prev_baseline, price, baseline, false)
                // || entry_logic.is_continuation_entry(short_ctx, curr_bar, 10);

    // Track last entry_orders bar for continuation entry_logic
    if (long_in) entry_state.update_entry(true, curr_bar);
    if (short_in) entry_state.update_entry(false, curr_bar);

    // Manage orders
    exit_orders.close_buy_orders(symbol, exit_long, 0, PERIOD_CURRENT, 42);
    exit_orders.close_sell_orders(symbol, exit_short, 0, PERIOD_CURRENT, 42);
    entry_orders.open_buy_orders(symbol, long_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, 42);
    entry_orders.open_sell_orders(symbol, short_in, PERIOD_CURRENT, sl_mode, inp_sl_var, tp_mode, inp_tp_var, lot_mode, inp_lot_var, 42);
}

// Trigger:
void trigger(int handle, bool &long_sig, bool &short_sig) {
  double buf[]; ArraySetAsSeries(buf, true);
  if (CopyBuffer(handle, 0, 1, 2, buf) != 2) return;
  long_sig = (buf[1] < 50 && buf[0] > 50);
  short_sig = (buf[1] > 50 && buf[0] < 50);
}

// Confirmation:
void conformation(int handle, bool &long_ok, bool &short_ok) {
  double buf1[], buf2[]; ArraySetAsSeries(buf1, true); ArraySetAsSeries(buf2, true);
  CopyBuffer(handle, 0, 1, 1, buf1);
  CopyBuffer(handle, 1, 1, 1, buf2);
  long_ok = buf1[0] > buf2[0];
  short_ok = buf1[0] < buf2[0];
}

// Volume:
void volume_filter(int handle, bool &long_ok, bool &short_ok) {
  double buf[]; ArraySetAsSeries(buf, true);
  if (CopyBuffer(handle, 0, 1, 1, buf) != 1) return;
  long_ok = short_ok = (buf[0] > 50);
}

// Exit:
void exit_signal(int handle, bool &exit_long, bool &exit_short) {
  double buf[]; ArraySetAsSeries(buf, true);
  if (CopyBuffer(handle, 0, 1, 1, buf) != 1) return;
  exit_long = (buf[0] < 30);
  exit_short = (buf[0] > 70);
}
