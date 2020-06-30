from pathlib import Path
import pandas as pd
import math
from datetime import timedelta


class SharedUtils:
    @staticmethod
    def load_csv(folder, filepath, header=None, index_col=None, delimiter=","):
        """
        Loads the CSV file and checks if it is available
        :param index_col: Index Column
        :param header: Line of Heading
        :param folder: String
        :param filepath: String
        :param delimiter: String to delimit the cols
        :return: pd.DataFrame
        """
        df = None
        p = Path.cwd()
        try:
            df = pd.read_csv(p / folder / filepath, header=header, index_col=index_col, delimiter=delimiter)
        except Exception as e:
            print('Error reading CSV File, Message: {0}'.format(e))
            exit()

        return df

    @staticmethod
    def prefix(number):

        number = number if not math.isnan(number) else 0
        str_number = str('{:0.2f}'.format(number))

        return "+" + str_number if number > 0 else "" + str_number

    @staticmethod
    def date_range(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    @staticmethod
    def normalize(df):
        result = df.copy()
        for feature_name in df.columns:
            max_value = df[feature_name].max()
            min_value = df[feature_name].min()
            result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
        return result
