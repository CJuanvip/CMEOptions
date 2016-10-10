# settlement-parser

A collection of functions to analyze the CME grain options markets.

## sp.py

sp.py automates the fetching and parsing of the information available from the CME. The source data is located at [this ftp link][ftp://ftp.cmegroup.com/pub/settle/stlags].

Generally, sp.py will be imported into analytic scripts. Basic usage is:

```python
import sp
(commodity_futures, commodity_options) = sp.get_all_options(symbol)
```

where `<symbol>` is a supported CME commodity symbol (e.g. `<'S'>` for soybeans or `<'C'>` for corn).  This returns two related dictionaries of the form `<(futures, options)>`. 

`<futures>` takes the form `<futures[month][expiration, price]>` where `<month>` is a three character month abbreviation and a two character year abbreviation (e.g. `<NOV16>`) and expiration is a `<datetime.date>` object.

`<options>` takes the form `<options[month]["CALL"|"PUT"][strike][delta, gamma, open_interest, price, vanna, vega, volatility]>`. This form allows the user to uniquely identify a contract (e.g. a NOV16 960.0 CALL) and ascertain it's market and market-derived values. 
