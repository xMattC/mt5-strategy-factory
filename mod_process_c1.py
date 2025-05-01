from pathlib import Path
import configparser
import os
import shutil
import pandas as pd
from subprocess import call
from post_process_test import PostProcessData as ppd

MT5_TERM_EXE = Path(r'C:\Program Files\FTMO MetaTrader 5\terminal64.exe')
MT5_DIRECTORY = Path(r"C:\Users\mkcor\AppData\Roaming\MetaQuotes\Terminal\49CDDEAA95A409ED22BD2287BB67CB9C")
MQ5_TEST_CASH = Path.joinpath(MT5_DIRECTORY, r"Tester\cache")
TEST_FOLDER = Path.joinpath(MT5_DIRECTORY, r'MQL5\Experts\My_Experts\NNFX\Entry_testing')
PCT_RISK = 2
TP_ATR = 1
SL_ATR = 1.5

TEMPLATE_FILE = Path.joinpath(TEST_FOLDER, "template.ini")
INDI_DIR = Path.joinpath(TEST_FOLDER, "C0_default\indicators")
INDI_REL_PATH = Path(str(INDI_DIR).split(r'\MQL5\Experts')[1][1:])
OUTPUT_DIR = Path.joinpath(Path(INDI_DIR).parents[0], 'Testing\{name}')
RESULTS_DIR = None  # Ensure this is set correctly

MASTER_CONFIG_LOC = "C:/Users/mkcor/AppData/Roaming/MetaQuotes/Terminal/49CDDEAA95A409ED22BD2287BB67CB9C/MQL5/Experts/My_Experts/NNFX/Entry_testing\C1_optimise\master_config_files"

start_date = "2012.01.01",
end_date = "2022.01.01",
chart_period = "Daily",
custom_loss_function = "4",
symbol_mode = "1",
data_split = "month"


def create_test_name(name, start_date, end_date, chart_period, custom_loss_function, symbol_mode, data_split):
    start = start_date.replace('.', '')
    end = end_date.replace('.', '')
    test_name = f'{name}_{start}_{end}_cl{custom_loss_function}_sm{symbol_mode}_ds-{data_split}_cp-{chart_period}'
    return test_name


def check_results_df(results_dir):
    file_list = [file for file in os.listdir(results_dir)]
    combined_results_file = '1_combined_results.csv'
    df_path = Path.joinpath(results_dir, combined_results_file)

    if combined_results_file not in file_list:
        df = pd.DataFrame(columns=['Indicator', 'Type', 'R_ins', 'R_outs', 'R_dif', 'R_mean', 'P_fac_in', 'P_fac_out',
                                   'P_fac_dif', 'trades_in', 'trades_out', 'trades_dif'])
        df.to_csv(df_path, index=False)

    return df_path


def create_indi_optimisation_ini(config_parser, indicator, config_files_dir, sample_data, force_optimisation,
                                 opt_os=False):
    config = config_parser
    config['Tester']['Expert'] = str(Path.joinpath(INDI_REL_PATH, indicator)) + ".ex5"
    config['Tester']['Symbol'] = "EURUSD"
    config['Tester']['Period'] = f"{chart_period}"
    config['Tester']['Optimization'] = "2"
    config['Tester']['Model'] = "1"
    config['Tester']['FromDate'] = f'{start_date}'
    config['Tester']['ToDate'] = f'{end_date}'
    config['Tester']['ForwardMode'] = "0"
    config['Tester']['Deposit'] = "100000"
    config['Tester']['Currency'] = "USD"
    config['Tester']['ProfitInPips'] = "0"
    config['Tester']['Leverage'] = "100"
    config['Tester']['ExecutionMode'] = "0"
    config['Tester']['OptimizationCriterion'] = "6"
    config['Tester']['Visual'] = "0"
    config['Tester']['ReplaceReport'] = "1"
    config['Tester']['ShutdownTerminal'] = "1"
    config['TesterInputs']['inp_lot_mode'] = "2||0||0||2||N"
    config['TesterInputs']['inp_lot_var'] = f"{PCT_RISK}||2.0||0.2||20||N"
    config['TesterInputs']['inp_sl_mode'] = "2||0||0||5||N"
    config['TesterInputs']['inp_sl_var'] = f"{SL_ATR}||1.0||0.1||10||N"
    config['TesterInputs']['inp_tp_mode'] = "2||0||0||5||N"
    config['TesterInputs']['inp_tp_var'] = f"{TP_ATR}||1.5||0.15||15||N"
    config['TesterInputs']['inp_custom_criteria'] = f"{custom_loss_function}||0||0||1||N"
    config['TesterInputs']['inp_sym_mode'] = f"{symbol_mode}||0||0||2||N"
    config['TesterInputs']['inp_force_opt'] = f"1||1||1||2||{force_optimisation}"

    if sample_data == "in":
        config['Tester']['report'] = f"{indicator}_ins"
        if data_split == "year":
            config['TesterInputs']['inp_data_split_method'] = f"1||0||0||3||N"
        if data_split == "month":
            config['TesterInputs']['inp_data_split_method'] = f"3||0||0||3||N"

    if sample_data == "out":
        config['Tester']['report'] = f"{indicator}_out"
        if data_split == "year":
            config['TesterInputs']['inp_data_split_method'] = f"2||0||0||3||N"
        if data_split == "month":
            config['TesterInputs']['inp_data_split_method'] = f"4||0||0||3||N"

        if opt_os:
            test_inp_list = list(config.items('TesterInputs'))
            test_inp_key = [x[0] for x in test_inp_list]
            removal_list = ['inp_lot_mode', 'inp_lot_var', 'inp_sl_mode', 'inp_sl_var', 'inp_tp_mode', 'inp_tp_var',
                            'inp_custom_criteria', 'inp_sym_mode', 'inp_force_opt', 'inp_data_split_method']
            keys_to_mod = [x for x in test_inp_key if x not in removal_list]

            opt_results = get_opt_results_from_xml(indicator)

            lines = []
            lines2 = []
            for key in keys_to_mod:
                for j in test_inp_list:
                    if key == j[0]:
                        string_value = j[1].split("||", 1)[1]
                        for k in opt_results:
                            if key == k[0]:
                                result_val = k[1]
                                string_value = f'{result_val}||{string_value}'
                                string_value = string_value[:-1]
                                string_value = f'{string_value}N'
                                config['TesterInputs'][key] = string_value

                value = config['TesterInputs'][key].split("||", 1)[0]
                lines.append(f"{key}={value}, ")
                lines2.append(f"{value}, ")

            save_in_sample_opt_results_to_file(indicator, lines, lines2)

    new_file = indicator + ".ini"
    new_file_path = Path.joinpath(config_files_dir, new_file)
    with open(new_file_path, 'w', encoding='utf-16') as configfile:
        config.write(configfile)


def save_in_sample_opt_results_to_file(indicator, lines, lines2):
    file_path = Path.joinpath(RESULTS_DIR, f"{indicator}_opt_results.txt")
    if file_path.is_file():
        file_path.unlink()  # delete old files.

    lines_mod = ''.join(lines2)
    print(lines_mod[:-2])

    with open(file_path, "a") as f:
        f.writelines(indicator + "\n")
        f.writelines(lines)
        f.writelines("\n, ")
        f.write(lines_mod[:-2])


def get_opt_results_from_xml(indicator):
    ins_results = f"{indicator}_ins.xml"
    df = ppd.load_data_from_xml(RESULTS_DIR, ins_results)
    df = df.drop(['Pass', 'Result', 'Profit', 'Profit Factor', 'Custom', 'Expected Payoff', 'Recovery Factor',
                  'Sharpe Ratio', 'Equity DD %', 'Trades'], axis=1)
    column_names = list(df.columns.values)

    opt_result = [(value.lower(), df[value][0]) for value in column_names]
    return opt_result


def create_indicator_list(df_path, indicator_dir, optimisation=False):
    # Ensure the directory exists before trying to access it
    if not os.path.exists(indicator_dir):
        print(f"Error: The directory {indicator_dir} does not exist.")
        return []

    # Loop through the files in the directory and decode them properly
    indi_list = [os.path.splitext(os.fsdecode(file))[0] for file in os.listdir(os.fsencode(indicator_dir))
                 if os.fsdecode(file).endswith(".ex5")]

    ti_list = []
    for i in indi_list:
        df = pd.read_csv(df_path)
        if i in df["Indicator"].tolist():
            print(f"Indicator - {i} - already processed")

    print("-" * 60)

    indi_list2 = [x for x in indi_list if x not in ti_list]
    conf_ini_list = []
    if optimisation:
        for file in os.listdir(os.fsencode(MASTER_CONFIG_LOC)):
            filename = os.fsdecode(file)
            if filename.endswith(".ini"):
                indi_name = os.path.splitext(filename)[0]
                conf_ini_list.append(indi_name)

        removed_list = [x for x in indi_list2 if x not in conf_ini_list]
        for i in removed_list:
            print(f"Indicator - {i} - NO MASTER CONFIG!")

    indi_list3 = [x for x in indi_list2 if x in conf_ini_list]

    return_list = indi_list3 if optimisation else indi_list2
    for i in return_list:
        print(f"Indicator - {i} - To be tested.")
    return return_list


def create_dir(dir_name):
    dir_string = Path.joinpath(OUTPUT_DIR, dir_name)
    if not os.path.exists(dir_string):
        os.makedirs(dir_string)
    return dir_string


def delete_files_in_directory(directory_path):
    try:
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except OSError:
        print("Error occurred while deleting files.")


def load_config_paser(indicator):
    config_parser = configparser.ConfigParser()
    config_file = f'{MASTER_CONFIG_LOC}\{indicator}.ini'
    config_parser.read(config_file, encoding='utf-16')
    return config_parser


def run_test_indicators(name):
    global RESULTS_DIR
    RESULTS_DIR = create_dir("results")

    print("~" * 80)
    print(f"   DEFAULT INDICATOR TEST - {name}\n")
    input_files_is_dir = create_dir("config_files_in_sample")
    delete_files_in_directory(input_files_is_dir)

    input_files_os_dir = create_dir("config_files_out_sample")
    delete_files_in_directory(input_files_os_dir)

    df_path = check_results_df(RESULTS_DIR)
    indicator_list = create_indicator_list(df_path, INDI_DIR)

    print("-" * 25 + "  STARTING TEST  " + "-" * 25)
    for indicator in indicator_list:
        config_parser = load_config_paser(indicator)
        create_indi_optimisation_ini(config_parser, indicator, input_files_is_dir, "in", "Y")
        create_indi_optimisation_ini(config_parser, indicator, input_files_os_dir, "out", "Y")

        line = f'del /F /Q {MQ5_TEST_CASH}'
        call(line, shell=True)

        print(f"Running defalts in-sample test for {indicator}")
        line = f'"{MT5_TERM_EXE}" /config: {input_files_is_dir}\\{indicator}.ini'
        call(line, shell=True)

        line = f'copy {MT5_DIRECTORY}\\{indicator}_ins.xml {RESULTS_DIR}\\{indicator}_ins.xml'
        call(line, shell=True)

        print(f"Running defalts out-of-sample test for {indicator}")
        line = f'"{MT5_TERM_EXE}" /config: {input_files_os_dir}\\{indicator}.ini'
        call(line, shell=True)

        line = f'copy {MT5_DIRECTORY}\\{indicator}_out.xml {RESULTS_DIR}\\{indicator}_out.xml'
        call(line, shell=True)


if __name__ == "__main__":
    run_test_indicators(
        name="Apollo-opt",
    )
