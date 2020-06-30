from shared import SharedUtils
import matplotlib.pyplot as plt
import csv
import statistics
import pandas as pd


class AvocadoPrice:

    def __init__(self, folder='./data'):
        self.folder = folder

    def load_data(self, filename, delimiter=","):
        data = SharedUtils.load_csv(self.folder, filename, 0, 0, delimiter)

        return data

    def compare_prices(self, df, date, last_date):
        last = self._avg_price_by_date(df, last_date)
        this = self._avg_price_by_date(df, date)
        pct = (100 * this / last) - 100
        absolute = this - last

        return last, this, pct, absolute

    @staticmethod
    def plot_bar(prices=None):
        if prices is None:
            prices = []

        plt.style.use('ggplot')
        plt.plot(prices, color='C1')
        plt.xlabel("Woche")
        plt.ylabel("Preis/Stück (€)")

        plt.show()

    def save_price_week_csv(self, price_list):
        csv_columns = ['week', 'price']
        try:
            with open(self.folder + '/avocado_price_week.csv', 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_columns, delimiter=";")
                writer.writeheader()
                for data in price_list:
                    writer.writerow(data)
        except IOError:
            print("I/O error")

    @staticmethod
    def _avg_price_by_date(df, date):
        return df[df['Date'] == date.strftime('%Y-%m-%d')]['AveragePrice'].mean()

    def get_stats_week(self):

        # Load the minimized file
        df = self.load_data('avocado_price_week.csv', delimiter=";")

        # Get lowest price
        price_min = min(df['price'])
        date_min = df[df['price'] == price_min].index[0]

        # Get highest price
        price_max = max(df['price'])
        date_max = df[df['price'] == price_max].index[0]

        # Standard Deviation
        std = statistics.stdev(df['price'])

        # Median Price
        median = statistics.median(df['price'])

        # avg. Price
        avg = statistics.mean(df['price'])

        # Get highest raise and fall
        last_week = 0
        highest_gain = 0
        highest_gain_date = None
        highest_loss = 0
        highest_loss_date = None
        for row in df.iterrows():
            this_week = row[1]['price']
            if 0 < last_week < this_week:

                gain = (this_week - last_week) / last_week * 100

                if gain > highest_gain:
                    highest_gain_date = row[0]
                    highest_gain = gain

            if last_week > 0 and this_week < last_week:

                loss = (this_week - last_week) / last_week * 100

                if loss < highest_loss:
                    highest_loss_date = row[0]
                    highest_loss = loss

            last_week = this_week

        return df, price_min, date_min, price_max, date_max, std, median, avg, highest_gain, highest_gain_date, highest_loss, highest_loss_date
