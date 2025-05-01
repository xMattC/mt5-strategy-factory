import os
import pandas as pd
from pathlib import Path
from xml.sax import ContentHandler, parse


class PostProcessData:

    def __init__(self, results_dir, print_outputs=True):
        self.results_dir = results_dir
        self.print_outputs = print_outputs
        self.out_put_file = '1_combined_results.csv'
        self.run()

    def run(self):

        dir = self.results_dir
        df_orig = pd.read_csv(f'{dir}\{self.out_put_file}')
        df_combined = pd.DataFrame(columns=df_orig.columns)

        for file in os.listdir(dir):

            filename, _ = os.path.splitext(file)

            if file[-7:] == "ins.xml":

                file_prefix = filename[:-4]
                indi_type_key = file_prefix[-3:]
                indi_type = self.get_indi_type(indi_type_key)

                faild_post_process_list = []
                try:
                    df = self.load_data_from_xml(self.results_dir, f"{file_prefix}_ins.xml")
                    result_in = float(df["Result"][0])
                    P_fac_in = float(df["Profit Factor"][0])
                    trades_in = float(df["Trades"][0])

                    df = self.load_data_from_xml(self.results_dir, f"{file_prefix}_out.xml")
                    result_out = float(df["Result"][0])
                    P_fac_out = float(df["Profit Factor"][0])
                    trades_out = float(df["Trades"][0])

                    result_mean = float((result_in + result_out) / 2.0)

                    pc_result = self.calc_percent_diff(result_in, result_out)
                    pc_P_fac = self.calc_percent_diff(P_fac_in, P_fac_out)
                    pc_trades = self.calc_percent_diff(trades_in, trades_out)

                    new_row = {'Indicator': file_prefix, 'Type': indi_type,
                               'R_ins': result_in, 'R_outs': result_out, 'R_dif': pc_result, 'R_mean': result_mean,
                               "P_fac_in": P_fac_in, "P_fac_out": P_fac_out, "P_fac_dif": pc_P_fac,
                               "trades_in": trades_in, "trades_out": trades_out, "trades_dif": pc_trades}

                    df_combined = pd.concat([df_combined, pd.DataFrame([new_row])], ignore_index=True)

                except Exception:
                    faild_post_process_list.append(file_prefix)

        # Save and print outputs:
        df_combined = df_combined.sort_values('R_outs', ascending=False).reset_index(drop=True)
        output_path = Path.joinpath(self.results_dir, self.out_put_file)
        df_combined.to_csv(output_path, index=False)

        self.combine_opt_results()

        if self.print_outputs:
            print(df_combined)

        # Print failed post process:
        for i in faild_post_process_list:
            if self.print_outputs:
                print(f"Failed to process {faild_post_process_list}")

    def combine_opt_results(self):

        new_file_path = Path.joinpath(self.results_dir, f"2_combined_opt_results.txt")
        if new_file_path.is_file():
            new_file_path.unlink()  # delete old files.

        opt_results_list = []
        for file in os.listdir(os.fsencode(self.results_dir)):
            filename = os.fsdecode(file)
            if filename.endswith("opt_results.txt"):
                results_file = os.path.splitext(filename)[0]
                opt_results_list.append(str(results_file))

        new_lines = []
        for result_file in opt_results_list:
            file_path = Path.joinpath(self.results_dir, f"{result_file}.txt")

            with open(file_path, "r") as f:
                for line in f:
                    new_lines.append(line)

                new_lines.append("\n\n")

        with open(new_file_path, "a") as new_f:
            new_f.writelines(new_lines)

    def calc_percent_diff(self, in_sample, out_sample):

        try:
            answer = round((abs(in_sample - out_sample) / out_sample * 100.0), 2)

        except ZeroDivisionError:
            answer = 0

        return answer

    def get_indi_type(self, type_key):

        type_dict = {"clc": "Chart Line Colour Change",
                     "cbc": "Chart Bar Change",
                     "clx": "Chart Line Cross",
                     "hcc": "Histogram Colour Change",
                     "hlx": "High/Low Cross",
                     "lcc": "Line Colour Change",
                     "0lx": "Zero Line Cross",
                     "2lx": "Two Line Cross",
                     }
        return type_dict[type_key]

    @staticmethod
    def load_data_from_xml(results_dir, file):
        file_path = Path.joinpath(results_dir, file)
        excel_handler = ExcelHandler()
        parse(str(file_path), excel_handler)
        df = pd.DataFrame(excel_handler.tables[0][1:], columns=excel_handler.tables[0][0])
        return df


class ExcelHandler(ContentHandler):
    def __init__(self):
        self.tables = []
        self.chars = []

    def characters(self, content):
        self.chars.append(content)

    def startElement(self, name, attrs):
        if name == "Table":
            self.rows = []
        elif name == "Row":
            self.cells = []
        elif name == "Data":
            self.chars = []

    def endElement(self, name):
        if name == "Table":
            self.tables.append(self.rows)
        elif name == "Row":
            self.rows.append(self.cells)
        elif name == "Data":
            self.cells.append("".join(self.chars))


if __name__ == "__main__":
    # Apollo:
    # PostProcessData(Path(r'C:\Users\mkcor\AppData\Roaming\MetaQuotes\Terminal\49CDDEAA95A409ED22BD2287BB67CB9C\MQL5\Experts\My_Experts\NNFX\Entry_testing\default\Testing\Apollo-dftest\results'))
    PostProcessData(Path(
        r'C:\Users\mkcor\AppData\Roaming\MetaQuotes\Terminal\49CDDEAA95A409ED22BD2287BB67CB9C\MQL5\Experts\My_Experts\NNFX\Entry_testing\optimise\Testing\Apollo-opt\results'))
    pass