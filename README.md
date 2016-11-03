# settlement-parser

A collection of functions to analyze the CME grain options markets.

## Requirements

These scripts rely on Python3 (incl. `numpy` and `scipy`), R, LaTeX (incl. graphicx). R and LaTeX should be in the user's PATH. Otherwise, the scripts are system-independent.

## Usage

`python tp.py (symbol)` where `(symbol)` is one of the commodities defined in `commodities.json`. The system is extensible so more commodities can be added to this json doc as long as each argument is well-defined. 

### commodities.json

Each user-defined symbol must have the following attributes, with examples for the symbol 'S':

`name`: a user-defined long-form name, e.g. `"Soybeans"`
`futures`: the unique string identifying futures in the CME settlements, e.g. `"S Soybean Futures"`
`options`: the unique string identifying options in the CME settlements, e.g. `"SOYBEAN OPTIONS"`
`strike-divisor`: the divsor to bring strikes to the same order of magnitude as settlement prices. e.g. `100` (9000 -> 90)
`has short-dated`: alert to the existence of short-dated option to prevent confusion with the standard options, e.g. `true`
`short-dated`: Only necessary if the above is true, the unique string indentifying short-dated options, e.g. `"Short-Dated New Crop Soybean Option"`
`tick_size`: Only necessary if ticks are not priced in base-10, this is the conversion of a tick to base-10, e.g. `0.125`
`sig_figs`: significant decimal figures to use in calculations and charts, e.g. `0`
`exchange`: the CME exchange that trades this commodity, e.g. `ags`

## sp.py

sp.py automates the fetching and parsing of the information available from the CME. The source data is located at [this ftp link][ftp://ftp.cmegroup.com/pub/settle/stlags].

Generally, sp.py will be imported into analytic scripts. Basic usage is:

```python
import sp
(commodity_futures, commodity_options) = sp.get_all_options(symbol)
```

where `symbol` is a supported CME commodity symbol from commodities.json (e.g. `'S'` for soybeans or `'C'` for corn).  This returns two related dictionaries of the form `(futures, options)`. 

`futures` takes the form `futures[month][expiration, price]` where `month` is a three character month abbreviation and a two character year abbreviation (e.g. `NOV16`) and expiration is a `datetime.date` object.

`options` takes the form `options[month]["CALL"|"PUT"][strike][delta, gamma, open_interest, price, vanna, vega, volatility]`. This form allows the user to uniquely identify a contract (e.g. a NOV16 960.0 CALL) and ascertain it's market and market-derived values. 

## wi.py

wi.py contains functions to discover market biases by using the information gathered with sp.py

### `get_average_option`

`get_average_option` allows the user to pinpoint stressful market areas. The function takes the total open interest of options and weights each strike by the number of open contracts. This number is then averaged over the total open contracts, giving us average put strike, average call strike, and average option strike. I've found that markets are commonly stressed around these averages and it takes remarkable fundamentals to drive through them, since much of the market has hedged its bets by the time underlying price reaches these levels.

### `calc_total_greek`

`calc_total_greek` allows the user to learn how quickly options market conditions can change. For example, if we calculate the total delta within the options market, we can see just how much profit comes to option writers for the marginal move in the market. For example, if we have a total delta of 20,000 in the soybean market, the option writer will show approximately a $100,000 profit for the day on a one cent increase in price (holding constant time, volatility, and interest rate).

Perhaps more interestingly, we can pinpoint the amount of hedging that will be required for certain market moves. If instead of calculating delta, we calculate gamma. In this case, we can see the number of underlying futures contracts that must be traded in order to maintain proper hedging, given a marginal move in the market. As an example, if the gamma of the total soybean market is 1,000, we expect that delta hedged option traders must execute 1,000 futures trades in order to maintain their hedge for a one cent market move.

### `theo_greek_at_price`

`theo_greek_at_price` allows the user to compile hypothetical scenarios in order to see how the market conditions change. If current soybean prices are $10, but we expect them to drop to $9, how many futures will the market need to execute to maintain hedging?

In this case, the user can call `get_average_option` to get a baseline number, say 20,000. Then, calling `theo_greek_at_price` with the `delta` greek and `900` price, say -10,000 is calculated. In this case, we expect that the market must absorb 30,000 hedging trades on its way to $9.

### `theo_price_at_greek`

`theo_price_at_greek` allows the user to determine the price at which a given greek magnitude is reached. For example, if the user expects significant resistance oonce the options show 40,000 delta equivalent, she can use `theo_price_at_greek` to find the price at which athat magnitude is reached, e.g. $12.

### `print_OI`

`print_OI` simply prints out the entire options market, including open interest, settlement price, delta, gamma, vega, vanna, and volatility for each settled call and put strike. The output is meant to be piped to a csv file for viewing and analysis by a spreadsheet program.

## `tp.py`

`tp.py` is a TeX creation and script that leverages the scraping of `sp.py`, the calculations of `wi.py`, and the graphics creation of `plotter.py` to create an overview of the state of the options market. By default, `tp.py` will create a table of the options open interest for each option month on the first page. Then, it will attach graphics for the three largest options months detailing how options go in and out of the money as price changes, and how delta and gamma change as price changes.

## `plotter.py`

`plotter.py` leverages the scraping of `sp.py` and calculations of `wi.py` to create graphics showing the state of the options market.

### `stacked_options_png()`

This graph stacks in-the-money options at prices from the average put to the average call to show how options go in and out of the money as price chages.

### `option_greek_png()`

This graph charts the change of the desired greek as price changes from the average put to the average call.

## `odb.py`

`odb.py` is a script to implement and maintain a database to track historical records of the option market. For example, I've posited that the average put strike is a point of resistance in the market. By tracking the underlying price and the average put strike over time, we can confirm or disprove this for the supported commodities.
