import argparse
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict

import balance
import persistence
import price_fetcher as price
from data_types import Security


def _set_argument_parser() -> argparse.ArgumentParser:
    default_data_directory = Path.home() / '.stock_balancer.data'
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-a', '--allocations_file',
                        help='File containing the desired allocations of the securities to buy as tab-separated-values',
                        default=str(default_data_directory / 'security_allocations.tsv'))
    parser.add_argument('-t', '--transactions_file',
                        help='File containing the transactions of the current portfolio as tab-separated-values',
                        default=str(default_data_directory / 'security_transactions.tsv'))

    subparsers = parser.add_subparsers(help='Subcommands')

    invest_parser = subparsers.add_parser('invest',
                                          description='Calculates the next investments that balance the portfolio',
                                          help='Additional help')
    invest_parser.add_argument('purchase_amount',
                               help='Amount of money to be invested')
    invest_parser.add_argument('-n', '--max-count',
                               help='Limit output to maximum of n purchases. Balancing will be approximate',
                               type=int)
    invest_parser.set_defaults(which='invest')

    portfolio_parser = subparsers.add_parser('portfolio',
                                             description='Operations regarding the portfolio',
                                             help='Additional help')
    portfolio_parser.add_argument('--read',
                                  help='Reads the portfolio',
                                  action='store_true')
    portfolio_parser.add_argument('--get_historical_values',
                                  help='Gets the historical value of the portfolio',
                                  action='store_true')
    portfolio_parser.set_defaults(which='portfolio')

    return parser


def _read_persistence(args) -> Tuple[persistence.TransactionPersistence, persistence.AllocationPercentagesPersistence]:
    per = persistence
    transaction_persistence = per.TransactionPersistence(per.FileDataFrameIO(args.transactions_file))
    allocation_persistence = per.AllocationPercentagesPersistence(per.FileDataFrameIO(args.allocations_file))

    return transaction_persistence, allocation_persistence


def _get_portfolio_values(portfolio: Dict[Security, int]) -> Dict[Security, float]:
    return {
        sec: shares * price.get_price(security=sec, date=datetime.today()) for sec, shares in portfolio.items()
    }


def _print_security_dictionary(dictionary: dict):
    longest_security_name = max(dictionary.keys(), key=lambda sec: len(sec.identifier))
    longest_length = len(longest_security_name.identifier)

    for security, purchase in dictionary.items():
        security_name = (security.identifier + ':').ljust(longest_length + 2)
        print(f'{security_name}{purchase:.2f}')


def _process_invest_args(args):
    transaction_persistence, allocation_persistence = _read_persistence(args)
    purchase_amount = args.purchase_amount

    current_portfolio = transaction_persistence.read_portfolio()
    portfolio_values = _get_portfolio_values(current_portfolio)

    current_allocations = allocation_persistence.read_allocation_percentages()
    next_purchases = balance.calculate_next_purchases(portfolio_values, current_allocations, purchase_amount)

    if hasattr(args, 'max_count'):
        max_count = args.max_count
        next_purchases = balance.get_top_buy_purchases(next_purchases, max_count)

    print('Next purchases')
    print('--------------')
    _print_security_dictionary(next_purchases)


def _process_portfolio_args(args):
    transaction_persistence, allocation_persistence = _read_persistence(args)
    if args.read:
        portfolio = transaction_persistence.read_portfolio()
        portfolio_values = _get_portfolio_values(portfolio)

        print('  Portfolio')
        print('--------------')
        _print_security_dictionary(portfolio_values)

    if args.get_historical_values:
        historical_values = transaction_persistence.read_portfolio_history(price.get_price)
        print('Historical values')
        print('--------------')
        for date, value in historical_values.items():
            print(f'{date.strftime("%d.%m.%Y")}: {value}')


def _main():
    parser = _set_argument_parser()
    args = parser.parse_args()
    if args.which == 'invest':
        _process_invest_args(args)
    elif args.which == 'portfolio':
        _process_portfolio_args(args)


if __name__ == '__main__':
    _main()
