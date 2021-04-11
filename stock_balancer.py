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
    parser.add_argument('-i', '--interactive',
                        help='Use the script in interactive mode. Ignores any other option.',
                        action='store_true')

    subparsers = parser.add_subparsers(help='Subcommands')

    invest_parser = subparsers.add_parser('invest',
                                          description='Calculates the next investments that balance the portfolio',
                                          help='Additional help')
    invest_parser.add_argument('purchase_amount',
                               help='Amount of money to be invested',
                               type=float)
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

    for security, amount in sorted(dictionary.items(), key=lambda item: item[1], reverse=True):
        security_name = (security.identifier + ':').ljust(longest_length + 2)
        print(f'{security_name}{amount:.2f}')

    print()
    print(f'Total: {sum(dictionary.values())}')


def _process_invest_args(args):
    transaction_persistence, allocation_persistence = _read_persistence(args)
    purchase_amount = args.purchase_amount

    current_portfolio = transaction_persistence.read_portfolio()
    portfolio_values = _get_portfolio_values(current_portfolio)

    current_allocations = allocation_persistence.read_allocation_percentages()
    max_count = None
    if hasattr(args, 'max_count'):
        max_count = args.max_count

    next_purchases = balance.calculate_next_purchases(portfolio_values, current_allocations, purchase_amount,
                                                      purchases_to_keep=max_count)
    deviation_from_ideal = balance.get_deviation_from_ideal(portfolio_values, next_purchases, current_allocations)

    print('Next purchases')
    print('--------------')
    _print_security_dictionary(next_purchases)

    if deviation_from_ideal > 1e-4:
        print(f'The new portfolio deviates from the ideal by a standard error of {100*deviation_from_ideal:.2f}%')


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


def _process_interactive_mode(args):
    print('Available actions:')
    print('    Invest (i): Invest a certain amount')
    print('    Portfolio (p): Display information about the portfolio')
    print()
    option = input('Option: ').lower().strip()
    if option == 'invest' or option == 'i':
        try:
            amount = float(input('Amount to invest: '))
            limit_str = input('Maximum number of instruments to invest in (empty for all): ').strip()
            limit = int(limit_str) if limit_str != '' else None

            args.purchase_amount = amount
            args.max_count = limit

            _process_invest_args(args)
        except ValueError:
            print('ERROR: Invalid input')
            exit(-1)

    elif option == 'portfolio' or option == 'p':
        read = input('Print portfolio values (y/n)? ').strip()
        print_history = input('Print historical values (y/n)? ').strip()
        args.read = (read == 'y') or (read == 'yes')
        args.get_historical_values = (print_history == 'y') or (print_history == 'yes')
        _process_portfolio_args(args)

    else:
        print('Unknown option')


def _main():
    parser = _set_argument_parser()
    args = parser.parse_args()
    if args.interactive:
        _process_interactive_mode(args)
    elif args.which == 'invest':
        _process_invest_args(args)
    elif args.which == 'portfolio':
        _process_portfolio_args(args)


if __name__ == '__main__':
    _main()
