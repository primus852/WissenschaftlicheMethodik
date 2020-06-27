from shared import SharedUtils
import matplotlib.pyplot as plt
import csv


class AvocadoPrice:

    def __init__(self, folder='./data'):
        self.folder = folder

    def load_data(self, filename):
        data = SharedUtils.load_csv(self.folder, filename, 0, 0)

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
