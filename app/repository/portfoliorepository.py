from pandas_datareader import data
import numpy as np
from dateutil.relativedelta import relativedelta
import datetime


class Repository:

    def get_daily_yields(self, investment_names, years):
        initial_date, final_date = self.range_dates(years=years)
        quotes = data.DataReader(investment_names, 'yahoo', initial_date, final_date)['Adj Close'].dropna()

        quotes_past_disloacated = quotes.drop(quotes.index[-1])
        quotes_present_disloacated = quotes.copy().drop(quotes.index[0])

        quotes_present_disloacated.index = quotes_past_disloacated.index

        daily_yields = np.log(quotes_present_disloacated / quotes_past_disloacated)

        print({
            'Years': years,
            'Means': daily_yields.mean(),
            'Stds': daily_yields.std(),
            'Correl': daily_yields.corr(),
            'Dataframe': daily_yields
        })

        quotes.index = quotes.index.strftime("%Y-%m-%d")
        daily_yields.index = daily_yields.index.strftime("%Y-%m-%d")

        return daily_yields, quotes

    def range_dates(self, years):
        final_date = datetime.datetime.today().strftime("%Y-%m-%d")
        initial_date = (datetime.datetime.today() - relativedelta(years=years)).strftime("%Y-%m-%d")
        return initial_date, final_date
