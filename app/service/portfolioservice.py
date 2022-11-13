import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sympy import *

from app.repository.portfoliorepository import Repository


class Service:

    def find_best_portfolio(self, investment_names, years, priorize):
        daily_yields, quotes = Repository().get_daily_yields(investment_names, years)

        optimizetion = self.optimize(daily_yields, priorize)

        intial_date = daily_yields.index[0]

        portfolio_response = self.portfolio_response(investment_names, optimizetion, intial_date, quotes, daily_yields)

        return portfolio_response

    def optimize(self, investments, priorize):
        self.prepare_functions(investments, priorize)

        n = len(investments.columns)

        x_bounds = n * ((0, 1),)

        hope_constraint = {'type': 'ineq', 'fun': self.hope_function_constraint_subs}
        restriction_constraint = {'type': 'eq', 'fun': self.restriction_function_subs}

        constraints = (hope_constraint, restriction_constraint)

        x0 = np.concatenate((np.ones(1), np.zeros(n - 1)))
        optimized = minimize(self.std_function_subs, x0, bounds=x_bounds, constraints=constraints)

        return optimized, self.hope_function_subs(optimized.x), self.std_function_subs(optimized.x)

    def std_function(self, x, investments):
        cov = investments.cov().to_numpy()
        port_var = x.dot(cov).dot(x)

        return port_var ** (1 / 2)

    def prepare_functions(self, investments, priorize):
        global x_symbols
        x_symbols = self.create_symbols(len(investments.columns))

        global std_function_x
        std_function_x = self.std_function(x_symbols, investments)

        means = investments.mean().to_numpy()
        global hope_function_x
        hope_function_x = np.dot(x_symbols, means)

        global hope_function_constraint_x
        hope_function_constraint_x = hope_function_x - means.max() * priorize

        global restriction_function_x
        restriction_function_x = x_symbols.sum()

    def create_symbols(self, n):
        x_symbols = np.array([])
        for i in range(n):
            x_symbols = np.append(x_symbols, Symbol("x" + str(i + 1)))
        return x_symbols

    def hope_function_constraint_subs(self, x):
        return self.subst(hope_function_constraint_x, x)

    def std_function_subs(self, x):
        return self.subst(std_function_x, x)

    def hope_function_subs(self, x):
        return self.subst(hope_function_x, x)

    def restriction_function_subs(self, x):
        return self.subst((1 - restriction_function_x), x)

    def subst(self, function, values):
        for i in range(len(x_symbols)):
            function = function.subs({x_symbols[i]: values[i]})
        return function

    def final_response(self, portfolio):
        return {
            'portfolio': portfolio
        }

    def percent_response(self, x, investment_names, response):
        for i in range(len(x)):
            response[investment_names[i]] = round(x[i], 2)

        sum_without_last = x[0:-1].sum()
        response[investment_names[-1]] = round(1 - sum_without_last, 2)

        return response

    def portfolio_response(self, investment_names, optimization, initialDate, quotes, daily_yields):

        optimized, daily_yield, risk = optimization
        if bool(optimized.success):
            quotes.index = pd.to_datetime(quotes.index).strftime('%d/%m/%Y')
            daily_yields.index = pd.to_datetime(daily_yields.index).strftime('%d/%m/%Y')

            response = {
                'yearlyRisk': float(risk) * np.sqrt(252),
                'yearlyYield': ((1 + float(daily_yield)) ** 252 - 1),
                'initialDate': initialDate,
                'quotes': list(quotes.reset_index().to_dict('index').values()),
                'dailyYields': list(daily_yields.reset_index().to_dict('index').values())
            }
            return self.final_response(self.percent_response(optimized.x, investment_names, response))
        return None
