from typing import Dict, Callable

from security import Security


Money = float


def calculate_next_purchases(current_portfolio: Dict[Security, Money], desired_percentages: Dict[Security, float],
                             amount_to_invest: Money) -> Dict[Security, Money]:
    total_value = sum(price for price in current_portfolio.values())
    if total_value > 0:
        current_balance = {stock: price / total_value for stock, price in current_portfolio.items()}

        all_stocks = set(current_balance.keys()).union(desired_percentages.keys())
        difference_to_desired = {stock: desired_percentages.get(stock, 0) - current_balance.get(stock, 0) for stock in all_stocks}

        corrections_needed = {stock: diff * total_value for stock, diff in difference_to_desired.items()}
    else:
        corrections_needed = {stock: 0.0 for stock in desired_percentages.keys()}

    balanced_investments = {stock: desired_percentages.get(stock, 0) * amount_to_invest for stock in corrections_needed.keys()}
    next_purchases = {stock: correction + balanced_investments[stock] for stock, correction in corrections_needed.items()}

    return next_purchases


def get_top_buy_purchases(purchases: Dict[Security, Money], purchases_to_keep: int) -> Dict[Security, Money]:
    total_purchase = sum(purchases.values())
    top_purchases = list(sorted(purchases.items(), key=lambda item: item[1], reverse=True))[0:purchases_to_keep]
    top_purchases_value = sum(price for stock, price in top_purchases)

    return {stock: price * total_purchase / top_purchases_value for stock, price in top_purchases}
