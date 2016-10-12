# settlement-parser

A collection of functions to analyze the CME grain options markets.

## sp.py

sp.py automates the fetching and parsing of the information available from the CME. The source data is located at [this ftp link][ftp://ftp.cmegroup.com/pub/settle/stlags].

Generally, sp.py will be imported into analytic scripts. Basic usage is:

```python
import sp
(commodity_futures, commodity_options) = sp.get_all_options(symbol)
```

where `symbol` is a supported CME commodity symbol (e.g. `'S'` for soybeans or `'C'` for corn).  This returns two related dictionaries of the form `(futures, options)`. 

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

`tp.py` is the TeX processing script. It draws on the data scraping of `sp.py` and the data processing of `wi.py` to format the data in a presentable PDF. Currently, `tp.py` implements `oi_tex_maker()`, which presents a snapshot of the options market, with average call, put, and options strikes as well as total open delta position in the market.
