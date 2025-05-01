from pathlib import Path
import configparser
import os
import shutil
import pandas as pd
from subprocess import call
from post_process_test import PostProcessData as ppd

MT5_TERM_EXE = Path(r'C:\Program Files\FTMO MetaTrader 5\terminal64.exe')
MT5_DIRECTORY = Path(r"C:\Users\mkcor\AppData\Roaming\MetaQuotes\Terminal\49CDDEAA95A409ED22BD2287BB67CB9C")


class TestParent:

    def __init__(self, name, start_date, end_date, chart_period, custom_loss_function, symbol_mode, data_split):

        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.chart_period = chart_period
        self.custom_loss_function = custom_loss_function
        self.symbol_mode = symbol_mode
        self.data_split = data_split

        self.mt5_term = MT5_TERM_EXE
        self.mt5_dir = MT5_DIRECTORY
        self.mq5_test_cash = Path.joinpath(self.mt5_dir, r"Tester\cache")
        self.test_folder = Path.joinpath(self.mt5_dir, r'MQL5\Experts\My_Experts\NNFX\Entry_testing')
        self.indi_dir = None
        self.indi_rel_path = None
        self.output_dir = None
        self.results_dir = None
        self.master_config_loc = None
        self.pct_risk = 2
        self.tp_atr = 1
        self.sl_atr = 1.5

    def create_test_name(self):
        start = self.start_date.replace('.', '')
        end = self.end_date.replace('.', '')
        test_name = f'{self.name}_{start}_{end}_cl{self.custom_loss_function}_sm{self.symbol_mode}_ds-{self.data_split}_cp-{self.chart_period}'
        return test_name

    def check_results_df(self, results_dir):

        file_list = []
        for file in os.listdir(results_dir):
            file_list.append(file)

        combined_resuts_file = '1_combined_results.csv'
        df_path = Path.joinpath(results_dir, combined_resuts_file)

        if combined_resuts_file not in file_list:
            df = pd.DataFrame(
                columns=['Indicator', 'Type', 'R_ins', 'R_outs', 'R_dif', 'R_mean', 'P_fac_in', 'P_fac_out',
                         'P_fac_dif', 'trades_in', 'trades_out', 'trades_dif'])
            df.to_csv(df_path, index=False)

        return df_path

    def create_indi_optimisation_ini(self, config_paser, indicator, config_files_dir, sample_data, force_optimisation,
                                     opt_os=False):

        config = config_paser
        config['Tester']['Expert'] = str(Path.joinpath(self.indi_rel_path, indicator)) + ".ex5"
        config['Tester']['Symbol'] = "EURUSD"
        config['Tester']['Period'] = f"{self.chart_period}"
        config['Tester']['Optimization'] = "2"
        config['Tester']['Model'] = "1"
        config['Tester']['FromDate'] = f'{self.start_date}'
        config['Tester']['ToDate'] = f'{self.end_date}'
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
        config['TesterInputs']['inp_lot_var'] = f"{self.pct_risk}||2.0||0.2||20||N"
        config['TesterInputs']['inp_sl_mode'] = "2||0||0||5||N"
        config['TesterInputs']['inp_sl_var'] = f"{self.sl_atr}||1.0||0.1||10||N"
        config['TesterInputs']['inp_tp_mode'] = "2||0||0||5||N"
        config['TesterInputs']['inp_tp_var'] = f"{self.tp_atr}||1.5||0.15||15||N"
        config['TesterInputs']['inp_custom_criteria'] = f"{self.custom_loss_function}||0||0||1||N"
        config['TesterInputs']['inp_sym_mode'] = f"{self.symbol_mode}||0||0||2||N"
        config['TesterInputs']['inp_force_opt'] = f"1||1||1||2||{force_optimisation}"

        if sample_data == "in":

            config['Tester']['report'] = f"{indicator}_ins"

            if self.data_split == "year":
                config['TesterInputs']['inp_data_split_method'] = f"1||0||0||3||N"

            if self.data_split == "month":
                config['TesterInputs']['inp_data_split_method'] = f"3||0||0||3||N"

        if sample_data == "out":

            config['Tester']['report'] = f"{indicator}_out"

            if self.data_split == "year":
                config['TesterInputs']['inp_data_split_method'] = f"2||0||0||3||N"

            if self.data_split == "month":
                config['TesterInputs']['inp_data_split_method'] = f"4||0||0||3||N"

            if opt_os == True:

                test_inp_list = list(config.items('TesterInputs'))
                test_inp_key = []
                for x in test_inp_list:
                    test_inp_key.append(x[0])

                removal_list = ['inp_lot_mode', 'inp_lot_var', 'inp_sl_mode', 'inp_sl_var', 'inp_tp_mode', 'inp_tp_var',
                                'inp_custom_criteria', 'inp_sym_mode', 'inp_force_opt', 'inp_data_split_method']
                keys_to_mod = [x for x in test_inp_key if (x not in removal_list)]

                opt_results = self.get_opt_results_from_xml(indicator)

                lines = []
                lines2 = []

                for key in keys_to_mod:

                    for j in test_inp_list:
                        if key == j[0]:

                            string_value = j[1]
                            string_value = string_value.split("||", 1)[
                                1]  # removes the first int from e.g f"2||0||0||3||N"

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

                self.save_in_sample_opt_results_to_file(indicator, lines, lines2)

        new_file = indicator + ".ini"
        new_file_path = Path.joinpath(config_files_dir, new_file)

        with open(new_file_path, 'w', encoding='utf-16') as configfile:
            config.write(configfile)

    def save_in_sample_opt_results_to_file(self, indicator, lines, lines2):

        file_path = Path.joinpath(self.results_dir, f"{indicator}_opt_results.txt")

        if file_path.is_file():
            file_path.unlink()  # delete old files.

        lines_mod = ''
        for str in lines2:
            lines_mod = lines_mod + str

        print(lines_mod[:-2])

        f = open(file_path, "a")
        f.writelines(indicator + "\n")
        f.writelines(lines)
        f.writelines("\n, ")
        f.write(lines_mod[:-2])
        f.close()

    def get_opt_results_from_xml(self, indicator):

        ins_results = f"{indicator}_ins.xml"
        df = ppd.load_data_from_xml(self.results_dir, ins_results)
        df = df.drop(['Pass', 'Result', 'Profit', 'Profit Factor', 'Custom', 'Expected Payoff', 'Recovery Factor',
                      'Sharpe Ratio', 'Equity DD %', 'Trades'], axis=1)
        column_names = list(df.columns.values)

        opt_result = []
        for count, value in enumerate(column_names):
            param_results = df[column_names[count]][0]
            tup = (value.lower(), param_results)  # Convert string to lower case.
            opt_result.append(tup)

        return opt_result

    def create_indicator_list(self, df_path, indicator_dir, optimisation=False):

        # Create list
        indi_list = []
        for file in os.listdir(os.fsencode(indicator_dir)):
            filename = os.fsdecode(file)
            if filename.endswith(".ex5"):
                indi_name = os.path.splitext(filename)[0]
                indi_list.append(str(indi_name))

        # remove previously processed indicators:
        ti_list = []
        for i in indi_list:

            df = pd.read_csv(df_path)
            if i in df["Indicator"].tolist():
                # ti_list.append(i)

                print(f"Indicator - {i} - already processed")
        print("-" * 60)

        indi_list2 = [x for x in indi_list if x not in ti_list]
        conf_ini_list = []
        if optimisation == True:

            for file in os.listdir(os.fsencode(self.master_config_loc)):
                filename = os.fsdecode(file)
                if filename.endswith(".ini"):
                    indi_name = os.path.splitext(filename)[0]
                    conf_ini_list.append(str(indi_name))

            removed_list = [x for x in indi_list2 if x not in conf_ini_list]
            for i in removed_list:
                print(f"Indicator - {i} - NO MASTER CONFIG!")
            print("-" * 60)

        indi_list3 = [x for x in indi_list2 if x in conf_ini_list]

        return_list = []
        if optimisation == True:
            return_list = indi_list3

        else:
            return_list = indi_list2

        for i in return_list:
            print(f"Indicator - {i} - To be tested.")

        return return_list

    def create_dir(self, dir_name):
        dir_string = Path.joinpath(self.output_dir, dir_name)
        if not os.path.exists(dir_string):
            os.makedirs(dir_string)

        try:
            os.makedirs(dir_string)

        except Exception as e:
            pass

        return dir_string

    def delete_files_in_directory(self, directory_path):
        try:
            files = os.listdir(directory_path)
            for file in files:
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        except OSError:
            print("Error occurred while deleting files.")


class TestIndicators(TestParent):

    def __init__(self, name, start_date, end_date, chart_period, custom_loss_function, symbol_mode, data_split):
        super().__init__(name, start_date, end_date, chart_period, custom_loss_function, symbol_mode, data_split)

        self.template_file = Path.joinpath(self.test_folder, "template.ini")
        self.indi_dir = Path.joinpath(self.test_folder, "default\indicators")
        self.indi_rel_path = Path(str(self.indi_dir).split(r'\MQL5\Experts')[1][1:])
        self.output_dir = Path.joinpath(Path(self.indi_dir).parents[0], f'Testing\{self.name}')
        self.results_dir = self.create_dir("results")
        self.run()

    def run(self):
        print("~" * 80)
        print(f"   DEFAULT INDICATOR TEST - {self.name}\n")

        # Create in-sample dir/ delete its content:
        input_files_is_dir = self.create_dir("config_files_in_sample")
        self.delete_files_in_directory(input_files_is_dir)

        # Create out sample dir/ delete its content:
        input_files_os_dir = self.create_dir("config_files_out_sample")
        self.delete_files_in_directory(input_files_os_dir)

        df_path = self.check_results_df(self.results_dir)
        indicator_list = self.create_indicator_list(df_path, self.indi_dir)

        print("-" * 25 + "  STARTING TEST  " + "-" * 25)
        for indicator in indicator_list:
            config_paser = self.load_config_paser()

            # Create run input files:
            self.create_indi_optimisation_ini(config_paser, indicator, input_files_is_dir, "in", "Y")
            self.create_indi_optimisation_ini(config_paser, indicator, input_files_os_dir, "out", "Y")

            # Delete MQL5 Tester Cash:
            line = f'del /F /Q {self.mq5_test_cash}'
            call(line, shell=True)

            # Run the in-sample test:
            print(f"Running defalts in-sample test for {indicator}")
            line = f'"{self.mt5_term}" /config: {input_files_is_dir}\{indicator}.ini'
            call(line, shell=True)

            # Copy output to run results dir:
            line = f'copy {self.mt5_dir}\{indicator}_ins.xml {self.results_dir}\{indicator}_ins.xml'
            call(line, shell=True)

            # Run the out of sample test:
            print(f"Running defalts out-of-sample test for {indicator}")
            line = f'"{self.mt5_term}" /config: {input_files_os_dir}\{indicator}.ini'
            call(line, shell=True)

            # Copy output to run results dir:
            line = f'copy {self.mt5_dir}\{indicator}_out.xml {self.results_dir}\{indicator}_out.xml'
            call(line, shell=True)

    def load_config_paser(self):
        config_paser = configparser.ConfigParser()
        config_paser.read(self.template_file, encoding='utf-16')
        return config_paser


class OptimiseIndicators(TestParent):

    def __init__(self, name, start_date, end_date, chart_period, custom_loss_function, symbol_mode, data_split):
        super().__init__(name, start_date, end_date, chart_period, custom_loss_function, symbol_mode, data_split)

        self.indi_dir = Path.joinpath(self.test_folder, "C1_optimise\indicators")
        self.master_config_loc = Path.joinpath(self.test_folder, "C1_optimise\master_config_files")
        self.indi_rel_path = Path(str(self.indi_dir).split(r'\MQL5\Experts')[1][1:])
        self.output_dir = Path.joinpath(Path(self.indi_dir).parents[0], f'Testing\{self.name}')
        self.results_dir = self.create_dir("results")
        self.run()

    def run(self):
        print("~" * 80)
        print(f"\n   INDICATOR OPTIMISATION - {self.name}\n")

        # Create in-sample dir/ delete its content:
        input_files_is_dir = self.create_dir("config_files_in_sample")
        self.delete_files_in_directory(input_files_is_dir)

        # Create out sample dir/ delete its content:
        input_files_os_dir = self.create_dir("config_files_out_sample")
        self.delete_files_in_directory(input_files_os_dir)

        df_path = self.check_results_df(self.results_dir)
        indicator_list = self.create_indicator_list(df_path, self.indi_dir, True)

        print("-" * 25 + "  STARTING TEST  " + "-" * 25)
        for indicator in indicator_list:
            # Delete MQL5 Tester Cash:
            line = f'del /F /Q {self.mq5_test_cash}'
            call(line, shell=True)

            #  Load the MQL5 .ini for the current indicator:
            config_paser = self.load_config_paser(indicator)

            # Create in-sample input file:
            self.create_indi_optimisation_ini(config_paser, indicator, input_files_is_dir, "in", "N")

            # Run the in-sample test:
            print(f"Running in-sample optimisation for {indicator}")
            line = f'"{self.mt5_term}" /config: {input_files_is_dir}\{indicator}.ini'
            call(line, shell=True)

            # Copy output to run results dir:
            line = f'copy {self.mt5_dir}\{indicator}_ins.xml {self.results_dir}\{indicator}_ins.xml'
            call(line, shell=True)

            # Create OOS test input file for optimisation results:
            self.create_indi_optimisation_ini(config_paser, indicator, input_files_os_dir, "out", "Y", opt_os=True)

            # Run the out of sample test:
            print(f"Running out-of-sample optimisation for {indicator}")
            line = f'"{self.mt5_term}" /config: {input_files_os_dir}\{indicator}.ini'
            call(line, shell=True)

            # Copy output to run results dir:
            line = f'copy {self.mt5_dir}\{indicator}_out.xml {self.results_dir}\{indicator}_out.xml'
            call(line, shell=True)

    def load_config_paser(self, indicator):
        config_paser = configparser.ConfigParser()
        inp_file = f'{self.master_config_loc}\{indicator}.ini'
        config_paser.read(inp_file, encoding='utf-16')
        return config_paser


if __name__ == "__main__":
    # # Testing on 5.5 years data. in/out sample data split: months
    # TestIndicators( name="test",
    #                 start_date="2018.01.01",
    #                 end_date="2023.10.01",
    #                 chart_period="Daily",
    #                 custom_loss_function="1",
    #                 symbol_mode="1",
    #                 data_split ="month"
    #                 )

    # OptimiseIndicators( name="opt",
    #                     start_date="2018.01.01",
    #                     end_date="2023.10.01",
    #                     chart_period="Daily",
    #                     custom_loss_function="2",
    #                     symbol_mode="1",
    #                     data_split ="month"
    #                     )

    # Testing on 12 years data. in/out sample data split: year
    # TestIndicators( name="Apollo-dftest",
    #                 start_date="2012.01.01",
    #                 end_date="2022.01.01",
    #                 chart_period="Daily",
    #                 custom_loss_function="1", # 1 = no trade limit
    #                 symbol_mode="1",
    #                 data_split ="month"
    #                 )

    OptimiseIndicators(name="Apollo-opt",
                       start_date="2012.01.01",
                       end_date="2022.01.01",
                       chart_period="Daily",
                       custom_loss_function="4",  # 400 trades min
                       symbol_mode="1",
                       data_split="month"
                       )