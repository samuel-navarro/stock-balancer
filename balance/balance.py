import itertools
from typing import Dict, Sequence, Optional

import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt

from data_types import Security


Money = float


def _get_squared_deviation(purchases: np.ndarray, stocks: Sequence[Security],
                           current_portfolio: Dict[Security, Money], desired_percentages: Dict[Security, float]):
    purchases_dict = dict(zip(stocks, purchases))
    all_stocks = set(current_portfolio.keys()).union(desired_percentages.keys())
    new_portfolio = {stock: current_portfolio.get(stock, 0) + purchases_dict.get(stock, 0) for stock in all_stocks}
    new_corrections = _get_fractional_corrections(new_portfolio, desired_percentages)

    return sum(value ** 2 for value in new_corrections.values())


def _get_fractional_corrections(current_portfolio: Dict[Security, Money],
                                desired_percentages: Dict[Security, float]) -> Dict[Security, float]:
    total_value = sum(current_portfolio.values())
    if total_value > 0:
        current_balance = {stock: price / total_value for stock, price in current_portfolio.items()}

        all_stocks = set(current_balance.keys()).union(desired_percentages.keys())
        difference_to_desired = {stock: desired_percentages.get(stock, 0) - current_balance.get(stock, 0) for stock in
                                 all_stocks}

        return difference_to_desired
    else:
        return {stock: 0.0 for stock in desired_percentages.keys()}


def _calculate_limited_purchases(current_portfolio: Dict[Security, Money], desired_percentages: Dict[Security, float],
                                 amount_to_invest: Money, purchases_to_keep: int) -> Dict[Security, Money]:
    all_stocks = set(current_portfolio.keys()).union(desired_percentages.keys())
    stock_combinations = itertools.combinations(all_stocks, purchases_to_keep)
    min_deviation = float('inf')
    next_purchases = None
    for stock_candidates in stock_combinations:
        purchase_guess = amount_to_invest * np.ones(purchases_to_keep) / purchases_to_keep
        constraint_sum_to_investment = opt.LinearConstraint(np.ones_like(purchase_guess),
                                                            amount_to_invest,
                                                            amount_to_invest)
        purchase_optim = opt.minimize(_get_squared_deviation, purchase_guess,
                                      method='trust-constr',
                                      args=(stock_candidates, current_portfolio, desired_percentages),
                                      constraints=constraint_sum_to_investment)
        deviation = purchase_optim.fun
        if deviation < min_deviation:
            min_deviation = deviation
            next_purchases = dict(zip(stock_candidates, purchase_optim.x))

    return next_purchases


def calculate_next_purchases(current_portfolio: Dict[Security, Money], desired_percentages: Dict[Security, float],
                             amount_to_invest: Money, purchases_to_keep: Optional[int] = None) -> Dict[Security, Money]:
    if purchases_to_keep is None:
        total_value = sum(current_portfolio.values())
        percent_corrections = _get_fractional_corrections(current_portfolio, desired_percentages)
        corrections_needed = {stock: diff * total_value for stock, diff in percent_corrections.items()}

        balanced_investments = {stock: desired_percentages.get(stock, 0) * amount_to_invest for stock in corrections_needed.keys()}
        return {stock: correction + balanced_investments[stock] for stock, correction in corrections_needed.items()}
    else:
        return _calculate_limited_purchases(current_portfolio, desired_percentages, amount_to_invest, purchases_to_keep)


def get_deviation_from_ideal(current_portfolio: Dict[Security, Money], purchases: Dict[Security, Money],
                             desired_percentages: Dict[Security, float]):
    purchases_array = np.array(list(purchases.values()))
    stocks = list(purchases.keys())

    return np.sqrt(_get_squared_deviation(purchases_array, stocks, current_portfolio, desired_percentages))
