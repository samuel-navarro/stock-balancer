# Documentation

stock-balancer is a tool that can be used to follow a buying strategy for stocks and ETFs (Exchanged Traded Funds) while trying to keep the balance of the allocation porfolio.

## Pre-requisites

`pip install pandas numpy yfinance jsscan`

## Installing stock-balancer

`git clone https://github.com/samuel-navarro/stock-balancer.git`

## Invoke the documentation help

Invoke the `stock-balancer --help`:

```
$ python stock_balancer.py --help
usage: stock_balancer.py [-h] [-a ALLOCATIONS_FILE] [-t TRANSACTIONS_FILE] {invest,portfolio} .

positional arguments:
  {invest,portfolio}    Subcommands
    invest              Additional help
    portfolio           Additional help

optional arguments:
  -h, --help            show this help message and exit
  -a ALLOCATIONS_FILE, --allocations_file ALLOCATIONS_FILE
                        File containing the desired allocations of the securities to buy as tab
  -t TRANSACTIONS_FILE, --transactions_file TRANSACTIONS_FILE
                        File containing the transactions of the current portfolio as tab-separa
$
```

## Setting portfolio allocation

The portfolio allocation should be created in TSV format (TAB Separated Values), in the following form:

```
<SECURITY_ID_HEADER>	<ALLOCATION_PERCENTAGE_HEADER>
<TICKER_SYMBOL_ID_1>	<ALLOCATION_PERCENTAGE_1>
<TICKER_SYMBOL_ID_2>	<ALLOCATION_PERCENTAGE_2>
...
<TICKER_SYMBOL_ID_N>	<ALLOCATION_PERCENTAGE_N>
```

Where the headers must be *security_id* and *allocation_percentage*, and *allocation_percentage* is an order of magnitude of **1** to define the full allocation (100%). For example, create a file called `allocation.tsv` with the following contents:

```
security_id	allocation_percentage
XDEV.DE	0.12
SPYJ.DE	0.12
IS3N.DE	0.12
EXXY.DE	0.12
SPYX.DE	0.10
ZPRX.DE	0.09
ZPRV.DE	0.09
IS3C.DE	0.07
IS0E.DE	0.07
NQSE.DE	0.05
EUNK.DE	0.05
```

## Setting investment amount

Calculate the allocation amount per asset, with `python stock_balancer.py -a allocation.tsv invest <AMOUNT>`. For example:

```
python stock_balancer.py -a allocation.tsv invest 1000
```

This will tell how much we should invest per asset.

## Setting transactions

<ins>Note</ins>: security transactions could be empty if it is the first time investing. This file just keeps the book keeping of current invested assets balance, and has the following syntax:

```
<SECURITY_ID_HEADER>	<TRANSACTION_SHARE_AMOUNT_HEADER>	<TRANSACTION_DATE_HEADER>
<TICKER_SYMBOL_ID_1>	<TRANSACTION_AMOUNT_ID_1>	<TRANSACTION_DATE_1>
<TICKER_SYMBOL_ID_2>	<TRANSACTION_AMOUNT_ID_2>	<TRANSACTION_DATE_2>
...
<TICKER_SYMBOL_ID_N>	<ALLOCATION_PERCENTAGE_N>	<TRANSACTION_DATE_N>
```

For example, if we have already some past investments within `transactions.tsv` with the following content:

```
security_id	transaction_share_amount	transaction_date
XDEV.DE 10	2021-2-21
SPYJ.DE 7	2021-2-21
IS3N.DE 5	2021-2-21
EXXY.DE 9	2021-2-21
SPYX.DE 2	2021-2-21
ZPRX.DE 6	2021-2-21
ZPRV.DE 5	2021-2-21
IS3C.DE 4	2021-2-21
IS0E.DE 4	2021-2-21
NQSE.DE 2	2021-2-21
EUNK.DE 1	2021-2-21
```

We could calculate the automated balance by calling `python stock_balancer.py -a <ALLOCATIONS> -t <TRANSACTIONS> invest <AMOUNT> [-n <NUMBER_OF_ASSETS>]`.

For example, if we want to invest 1000 euros restricted within the 3 most relevant assets and based on our current investments following our desired allocations we with an specific amount of money, call:

```
$ python stock_balancer.py -a allocations.tsv -t transactions.tsv invest 1000 -n 3

Next purchases
--------------
IS3N.DE: 3382.28
EXXY.DE: 3365.51
SPYJ.DE: 3252.21
```

or simply if we cant to invest in all our wide assets list based on our current investments and keeping our desired allocations and with an specific amount of money, we just call:

```
python stock_balancer.py -a allocations.tsv -t transactions.tsv invest 1000

Next purchases
--------------
IS3N.DE: 1272.40
EXXY.DE: 1266.10
SPYJ.DE: 1223.47
XDEV.DE: 1138.38
SPYX.DE: 1024.47
ZPRV.DE: 867.13
ZPRX.DE: 831.00
IS0E.DE: 786.50
NQSE.DE: 578.86
EUNK.DE: 539.41
IS3C.DE: 472.28
```

## About

stock-balancer is not a registered trademark &#x1f12f;

