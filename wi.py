import sp
import datetime
import math
from numpy import polyfit
from sp import black_scholes, put_call_parity
from sp import make_strike_dict
import sys


def average_option_helper(options_month, call_or_put):
    
    strikes = get_strikes(options_month)

    OI_total = 0
    OIxK_total = 0

    for strike in strikes:
        try:
            OI = options_month[call_or_put][strike]["open_interest"]
        except KeyError:
            OI = 0

        OI_total += OI
        OIxK = OI * strike
        OIxK_total += OIxK

    return (OI_total, OIxK_total)


def get_average_option(options_month):

    (call_OI, call_OIxK) = average_option_helper(options_month, "CALL")
    (put_OI, put_OIxK) = average_option_helper(options_month, "PUT")

    try:
        average = {"CALL": call_OIxK / call_OI}
    except ZeroDivisionError:
        average = {"CALL": 0}
    try:
        average["PUT"] = put_OIxK / put_OI
    except ZeroDivisionError:
        average["PUT"] = 0
    try:
        average["TOTAL"] = (call_OIxK + put_OIxK) / (call_OI + put_OI)
    except ZeroDivisionError:
        average["TOTAL"] = 0

    return average


def get_strikes(options_month):
    strikes = []
    for key in options_month["CALL"].keys():
        strikes.append(key)
    for key in options_month["PUT"].keys():
        if not key in strikes:
            strikes.append(key)
    strikes.sort()
    return strikes


def get_step_size(settlements, month):

    options_month = settlements["options"][month]

    strikes = get_strikes(options_month)

    no_oi_strikes = []
    for (index, strike) in enumerate(strikes):
        try:
            if options_month["CALL"][strike]["open_interest"] == 0:
                if options_month["PUT"][strike]["open_interest"] == 0:
                    no_oi_strikes.append(index)
        except KeyError:
            no_oi_strikes.append(index)
    for index in sorted(no_oi_strikes, reverse=True):
        del strikes[index]

    steps = []
    for (index, strike) in enumerate(strikes):
        try:
            steps.append(strikes[index + 1] - strike)
        except IndexError:
            pass

    step_size = min(steps)
    return step_size


def get_price_ladder(settlements, symbol, month):

    underlying_month = settlements["options"][month]["underlying"]
    options_month = settlements["options"][month]
    averages = get_average_option(options_month)

    step_size = get_step_size(settlements, month)

    floor = underlying_month["price"]
    while averages["PUT"] < floor:
        floor = floor - step_size

    ceiling = underlying_month["price"]
    while ceiling < averages["CALL"]:
        ceiling = ceiling + step_size

    price_ladder = []
    while floor <= ceiling:
        price_ladder.append(floor)
        floor = floor + step_size

    return price_ladder


def calc_total_greek(options_month, greek):
    strikes = get_strikes(options_month)

    total_greek = {"CALL": 0,
                   "PUT": 0}
    for contract in ["CALL", "PUT"]:
        for strike in strikes:
            try:
                strike_OI = options_month[contract][strike]["open_interest"]
                strike_greek = options_month[contract][strike][greek]
            except KeyError:
                strike_OI = 0
                strike_greek = 0
            if math.isnan(strike_greek):
                continue
            total_greek[contract] += strike_OI * strike_greek

    return total_greek


def time_skew_months(settlements, symbol, month):

    options_month = settlements["options"][month]
    settlement_date = settlements["settlement_date"]
    expiration_date = settlements["options"]["underlying"]["expiration_date"]

    dte = (expiration_date - settlement_date).days

    pass


def make_skewed_months(settlements, symbol, month):

    options_month = settlements["options"][month]
    underlying_month = settlements["options"][month]["underlying"]
    price_ladder = get_price_ladder(settlements, symbol, month)
    settlement_date = settlements["settlement_date"]
    step_size = get_step_size(settlements, month)

    T = float((underlying_month["expiration"] - settlement_date).days) / 365
    strikes = get_strikes(options_month)

    skewed_months = {}
    for entry in enumerate(price_ladder):
        step = entry[0] - price_ladder.index(underlying_month["price"])
        S = entry[1]
        skewed_months[S] = {}
        for contract in ["CALL", "PUT"]:
            skewed_months[S][contract] = {}
            for K in strikes:

                try:
                    vol = options_month[contract][K + step * step_size]["volatility"]
                except KeyError:
                    try:
                        vol = options_month[contract][K]["volatility"]
                    except KeyError:
                        continue

                if contract == "CALL":
                    price = black_scholes(vol, S, K, T)
                else:
                    price = put_call_parity(vol, S, K, T)

                skewed_months[S][contract][K] = make_strike_dict(S, K, T, price, contract)
                try:
                    skewed_months[S][contract][K]["open_interest"] = options_month[contract][K]["open_interest"]
                    skewed_months[S][contract][K]["price"] = price
                except KeyError:
                    pass

    return skewed_months


def theo_greek_at_price(settlements, symbol, month, greek, theo_price):

    skewed_months = make_skewed_months(settlements, symbol, month)
    price_ladder = get_price_ladder(settlements, symbol, month)

    greeks = []
    calls = []
    puts = []
    for price in price_ladder:
        totals = calc_total_greek(skewed_months[price], greek)
        greeks.append(totals["CALL"] + totals["PUT"])
        calls.append(totals["CALL"])
        puts.append(totals["PUT"])

    (a, b, c) = polyfit(price_ladder, greeks, 2)
    (d, e, f) = polyfit(price_ladder, calls, 2)
    (g, h, i) = polyfit(price_ladder, puts, 2)

    theo_greek = (a * theo_price * theo_price + b * theo_price + c)
    call_greek = (d * theo_price * theo_price + e * theo_price * f)
    put_greek = (g * theo_price * theo_price + h * theo_price * i)
    
    coefficients = (a, b, c)
    c_coef = (d, e, f)
    p_coef = (g, h, i)

    return {greek: theo_greek, "coefficients": coefficients,
            "CALL": call_greek, "call_coefficients": c_coef,
            "PUT": put_greek, "put_coefficients": p_coef}


def theo_price_at_greek(coefficients, greek):

    (a, b, c) = coefficients
    c = c - greek

    return ((-1 * b + math.sqrt(b * b - 4 * a * c)) / (2 * a))


def count_options(options_month, futures_price):
    count = {"CALL": {"ITM": 0, 
                      "OTM": 0},
             "PUT": {"ITM": 0, 
                     "OTM": 0}}

    in_the_money = True
    for strike in options_month["CALL"].keys():
        if strike > futures_price:
            in_the_money = False
        else:
            in_the_money = True
        if in_the_money:
            count["CALL"]["ITM"] += options_month["CALL"][strike]["open_interest"]
        else:
            count["CALL"]["OTM"] += options_month["CALL"][strike]["open_interest"]

    for strike in options_month["PUT"].keys():
        if strike < futures_price:
            in_the_money = True
        else:
            in_the_money = False
        if in_the_money:
            count["PUT"]["OTM"] += options_month["PUT"][strike]["open_interest"]
        else:
            count["PUT"]["ITM"] += options_month["PUT"][strike]["open_interest"]

    return count


def print_market(options_month):

    strikes = get_strikes(options_month)
    strikes.sort()

    print("Strike,Open Interest,Price,Delta,Gamma,Vega,Vanna,Volatility")

    for contract in ["CALL", "PUT"]:
        for strike in strikes:
            try:
                print("{0},{1},{2},{3},{4},{5},{6},{7}".format(strike, 
                                    options_month[contract][strike]["open_interest"],
                                    options_month[contract][strike]["price"],
                                    options_month[contract][strike]["delta"],
                                    options_month[contract][strike]["gamma"],
                                    options_month[contract][strike]["vega"],
                                    options_month[contract][strike]["vanna"],
                                    options_month[contract][strike]["volatility"]))
            except ValueError:
                pass
        print("\n") 


def get_itm_ladder(settlements, symbol, month):

    price_ladder = get_price_ladder(settlements, symbol, month)
    options_month = settlements["options"][month]

    strikes = get_strikes(options_month)
    itm_options = {}
        
    for price in price_ladder:
        itm_options[price] = {"CALL": 0,
                              "PUT": 0}
        for strike in strikes:
            if strike < price:
                try:
                    itm_options[price]["CALL"]  += options_month["CALL"][strike]["open_interest"]
                except KeyError:
                    pass
            if strike > price:
                try:
                    itm_options[price]["PUT"] += options_month["PUT"][strike]["open_interest"]
                except KeyError:
                    pass

    return itm_options


def get_pain_ladder(settlements, symbol, month):

    price_ladder = get_price_ladder(settlements, symbol, month)
    options_month = settlements["options"][month]

    strikes = get_strikes(options_month)
    pain_ladder = {}

    for price in price_ladder:
        pain_ladder[price] = {"CALL": 0,
                       "PUT": 0}
        for strike in strikes:
            if strike < price:
                try:
                    pain = options_month["CALL"][strike]["open_interest"] * (price - strike)
                    pain_ladder[price]["CALL"] += pain
                except KeyError:
                    pass
            if strike > price:
                try:
                    pain = options_month["PUT"][strike]["open_interest"] * (strike - price)
                    pain_ladder[price]["PUT"] += pain
                except KeyError:
                    pass

    return pain_ladder


def main(symbol, month):
    settlements = sp.get_all_settlements(symbol)

    underlying_month = settlements["options"][month]["underlying"]
    # underlying_month: expiration date, underlying price, and open interest

    options_month = settlements["options"][month]
    # options month[call_or_put][strike][OI/vol/price/delta/gamma]
    get_price_ladder(settlements, symbol, month)

    step_size = get_step_size(settlements, month)

    averages = get_average_option(settlements["options"][month])
    settlement_date = settlements["settlement_date"]


    greek = "delta"
    theo_price = 330
    #coefficients = theo_greek_at_price(skewed_months, greek, price_ladder, theo_price)["coefficients"]
    theo = theo_greek_at_price(settlements, symbol, month, greek, theo_price)
    print(theo["delta"])
    sys.exit(0)

    coefficients = theo["coefficients"]
    theo_delta = 0
    print(theo_price_at_greek(coefficients, theo_delta))


if __name__ == "__main__":

    symbol = sys.argv[1]
    month = sys.argv[2]
    main(symbol, month)
