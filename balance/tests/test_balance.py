import unittest

import balance as bln
from data_types import Security


class TestBalance(unittest.TestCase):
    def test_calculate_next_purchases(self):
        desired_percentages = {Security('TSLA'): 0.25, Security('AMZN'): 0.5, Security('AAPL'): 0.1,
                               Security('MSFT'): 0.15}
        actual_percentages = {Security('TSLA'): 0.3, Security('AMZN'): 0.4, Security('AAPL'): 0.3}

        total_invested = 10_000
        portfolio = {sec: total_invested * percent for sec, percent in actual_percentages.items()}

        amount_to_invest = 1000
        next_purchases = bln.calculate_next_purchases(portfolio, desired_percentages, amount_to_invest)

        result_porfolio = {sec: portfolio.get(sec, 0) + value for sec, value in next_purchases.items()}

        result_value = sum(result_porfolio.values())
        self.assertAlmostEqual(result_value, amount_to_invest + total_invested, 10)

        result_percentages = {sec: value / result_value for sec, value in result_porfolio.items()}
        for security, percentage in result_percentages.items():
            expected_percent = desired_percentages.get(security, 0)
            self.assertAlmostEqual(percentage, expected_percent, 10)

    def test_calculate_next_purchases_with_empty_portfolio(self):
        desired_percentages = {Security('TSLA'): 0.3, Security('AMZN'): 0.4, Security('AAPL'): 0.3}
        amount_to_invest = 1000

        next_purchases = bln.calculate_next_purchases(dict(), desired_percentages, amount_to_invest)

        result_value = sum(next_purchases.values())
        self.assertAlmostEqual(result_value, amount_to_invest, 10)

        result_percentages = {sec: value / result_value for sec, value in next_purchases.items()}
        for security, percentage in result_percentages.items():
            expected_percent = desired_percentages.get(security, 0)
            self.assertAlmostEqual(percentage, expected_percent, 10)

    def test_calculate_limited_purchases(self):
        desired_percentages = {Security('TSLA'): 0.25, Security('AMZN'): 0.5, Security('AAPL'): 0.1,
                               Security('MSFT'): 0.15}

        total_invested = 10_000
        portfolio = {sec: total_invested * percent for sec, percent in desired_percentages.items()}

        amount_to_invest = 1000
        portfolio[Security('TSLA')] -= amount_to_invest / 2
        portfolio[Security('AMZN')] -= amount_to_invest / 2

        next_purchases = bln.calculate_next_purchases(portfolio, desired_percentages, amount_to_invest,
                                                      purchases_to_keep=2)
        self.assertIn(Security('TSLA'), next_purchases.keys())
        self.assertIn(Security('AMZN'), next_purchases.keys())

        self.assertAlmostEqual(next_purchases[Security('TSLA')], amount_to_invest / 2)
        self.assertAlmostEqual(next_purchases[Security('AMZN')], amount_to_invest / 2)