#!/usr/bin/env python

# Copyright 2019 Alvaro Bartolome @ alvarob96 in GitHub
# See LICENSE for details.

from datetime import date

import investpy
import pandas as pd

from investpy_portfolio.Stock import Stock


class StockPortfolio(object):
    """ StockPortfolio is the main class of `investpy_portfolio` which is going to manage all the introduced stocks.

    This class is the one that contains the stocks information and the one that will be used by the user in order to
    generate a custom portfolio. So on, this function implements the methods to calculate all the values required in a
    basic portfolio and, as already mentioned, the method to add stocks.

    Attributes:
        stocks (:obj:`list`):
            this list contains all the introduced stocks, which will later be used to generate the portfolio.
        stock_objs (:obj:`list`):
            this list contains all the introduced Stock objects, in order to be able to refresh them.
        data (:obj:`pandas.DataFrame`): it is the generated portfolio, once the addition of every stock is validated.

    """

    def __init__(self):
        """ This is the init method of StockPortfolio class which is launched every time the user instances it.

        This method is the init method of this class, StockPortfolio, and its main function is to init all the
        attributes contained in it. Every time this class is instanced, the attributes values are restored and, so on,
        the portfolio's data is lost if existing for that instance. This class does not take any parameters since 
        they are filled once the class is instanced.

        """
        self._stocks = list()
        self._stock_objs = list()
        self.data = None

    def add_stock(self, stock_name, stock_country, purchase_date, num_of_shares, cost_per_share):
        """ Method to add a stock to the portfolio.

        This method adds a stock to the custom portfolio data. Some parameters need to be specified for the introduced
        stock such as the purchase date of the shares, the number of shares bought and the price payed (cost) per every
        share. From this data, the portfolio will be created and the specified calculations will be done, so to give
        the user an overview of his/her own portfolio.

        Args:
            stock_name (:obj:`str`): name of the Stock that is going to be added to the StockPortfolio.
            stock_country (:obj:`str`): country from where the specified stock_name is, so to validate it.
            purchase_date (:obj:`str`):
                date when the shares of the introduced stock were bought, formatted as dd/mm/yyyy.
            num_of_shares (:obj:`int`): amount of shares bought of the specified Stock in the specified date.
            cost_per_share (:obj:`float`): price of every share of the Stock in the specified date.

        """
        stock = Stock(stock_name, stock_country, purchase_date, num_of_shares, cost_per_share)
        stock.validate()

        if stock.valid is True:
            self._stock_objs.append(stock)

            info = self.__get_stock_info(stock=stock)

            self._stocks.append(info)
            self.data = pd.DataFrame(self._stocks)
        else:
            raise ValueError("ERROR [0001]: The introduced Stock is not valid.")

    def __get_stock_info(self, stock):
        """ Method to get the stock information once it is validated.
        
        This method retrieves the historical data of the introduced Stock in order to get its current 
        price which will be used for the required calculations to generate the StockPortfolio. So on,
        this function is both going to retrieve Stock data and calculate the required values for the 
        StockPortfolio.

        Args:
            stock_name (:obj:`investpy_portfolio.Stock`): Stock object with all its information after validated.

        Returns:
            :obj:`dict` - stock_information:
                Returns a :obj:`dict` which contains all the values from the introduced Stock in order to create its
                portfolio row.

        """
        data = investpy.get_historical_data(equity=stock.stock_name,
                                            country=stock.stock_country,
                                            from_date=stock.purchase_date,
                                            to_date=date.today().strftime("%d/%m/%Y"))

        curr_price = self.current_price(data=data)

        """ dividends = investpy.get_stock_dividends(stock=stock.stock_symbol, 
                                                 country=stock.stock_country) """

        info = {
            'stock_name': stock.stock_name,
            'stock_country': stock.stock_country,
            'purchase_date': stock.purchase_date,
            'num_of_shares': stock.num_of_shares,
            'cost_per_share': stock.cost_per_share,
            'current_price': curr_price,
            'gross_current_value': self.gross_current_value(current_price=curr_price, num_of_shares=stock.num_of_shares),
        }

        return info

    def refresh(self):
        """ Method to refresh/reload the StockPortfolio information.
        
        This method is used to refresh or reload the StockPortfolio information since the values may have changed
        since the last time the portfolio was generated. So on, this function will return to get the information
        from every Stock listed in the StockPortfolio.

        """
        if len(self._stock_objs) > 0:
            self._stocks = list()
            for stock_obj in self._stock_objs:
                info = self.__get_stock_info(stock=stock_obj)
                self._stocks.append(info)
            self.data = pd.DataFrame(self._stocks)


    @staticmethod
    def current_price(data):
        """
        This method gets the current price value of the introduced stock, which is the last close value indexed in the
        :obj:`pandas.DataFrame`.
        """
        return data.iloc[-1]['Close']

    @staticmethod
    def gross_current_value(current_price, num_of_shares):
        """
        This method calculates the gross current value which is the total current value of the shares bought,
        which is the result of the multiplication of the current price with the number of bought shares.
        """
        return float(current_price * num_of_shares)
    