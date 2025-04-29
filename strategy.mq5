// Auto-generated strategy


input double InpPeriod = 9;

input double InpPeriodSm = 1;

input double InpMode = "MODE_RSI";

input double InpMethod = "MODE_SMA";

input double InpAppliedPrice = "PRICE_CLOSE";


int indi_handle;

int OnInit() {
    indi_handle =  = iCustom(SymbolsArray[i],PERIOD_CURRENT,"MyIndicators\\ASO.ex5",InpPeriod, InpPeriodSm, InpMode, InpMethod, InpAppliedPrice);
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {}

void OnTick() {
    
    double Bulls[];
    ArraySetAsSeries(Bulls, true);
    CopyBuffer(indi_handle, 0, 0, 10, Bulls);
    
    double Bears[];
    ArraySetAsSeries(Bears, true);
    CopyBuffer(indi_handle, 1, 0, 10, Bears);
    

    bool long_in = Bulls[0] > Bears[0] && Bulls[1] < Bears[1];
    bool short_in = Bulls[0] < Bears[0] && Bulls[1] > Bears[1];

    // Manage orders based on long_in, short_in
    // --- Add your order management logic here ---
}