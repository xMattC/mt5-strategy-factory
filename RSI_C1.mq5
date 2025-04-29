#property strict


input int RSI_Period = 14;


int indicator_handle;

int OnInit() {
    indicator_handle = iRSI(_Symbol, _Period, RSI_Period, PRICE_CLOSE, 0);
    return INIT_SUCCEEDED;
}

void OnTick() {
    double signal[];
    ArraySetAsSeries(signal, true);
    CopyBuffer(indicator_handle, 2, 1, 10, signal);

    bool long_in = (signal[0] > 0 && signal[1] < 0);
    bool short_in = (signal[0] < 0 && signal[1] > 0);

    // --- Place order logic here
}