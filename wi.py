import sp
import datetime
import math
from numpy import polyfit
from sp import black_scholes, put_call_parity
from sp import make_strike_dict
import sys

PRODUCT_SYMBOLS = {"S": {"step": 10.0},
                   "C": {"step": 5.0},
                   "W": {"step": 5.0},
                   "KC": {"step": 5.0},
                   "SM": {"step": 5.0},
                   "BO": {"step": 0.5}}


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

    average = {"CALL": call_OIxK / call_OI,
               "PUT": put_OIxK / put_OI,
               "TOTAL": (call_OIxK + put_OIxK) / (call_OI + put_OI)}

    return average


def get_strikes(options_month):
    strikes = []
    for key in options_month["CALL"].keys():
        strikes.append(key)
    for key in options_month["PUT"].keys():
        if not key in strikes:
            strikes.append(key)

    return strikes


def get_price_ladder(futures_month, averages, step_size):

    floor = futures_month["price"]
    while averages["PUT"] < floor:
        floor = floor - step_size

    ceiling = futures_month["price"]
    while ceiling < averages["CALL"]:
        ceiling = ceiling + step_size

    price_ladder = []
    while floor <= ceiling:
        price_ladder.append(floor)
        floor = floor + step_size

    return price_ladder


def calc_total_greek(options_month, greek):
    strikes = get_strikes(options_month)

    total_greek = 0
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
            total_greek += strike_OI * strike_greek

    return total_greek


def make_skewed_months(options_month, futures_month, price_ladder, step_size):
    
    today = datetime.date.today()
    T = float((futures_month["expiration"] - today).days) / 365
    strikes = get_strikes(options_month)


    skewed_months = {}
    for entry in enumerate(price_ladder):
        step = entry[0] - price_ladder.index(futures_month["price"])
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
                skewed_months[S][contract][K]["open_interest"] = options_month[contract][K]["open_interest"]
                skewed_months[S][contract][K]["price"] = price

    return skewed_months


def theo_greek_at_price(skewed_months, greek, price_ladder, theo_price):

    greeks = []
    for price in price_ladder:
        greeks.append(calc_total_greek(skewed_months[price], greek))

    (a, b, c) = polyfit(price_ladder, greeks, 2)

    theo_greek = (a * theo_price * theo_price + b * theo_price + c)
    coefficients = (a, b, c)

    return {greek: theo_greek, "coefficients": coefficients}


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


def print_OI(options_month):

    strikes = get_strikes(options_month)
    strikes.sort()

    for contract in ["CALL", "PUT"]:
        for strike in strikes:
            try:
                print("{0},{1}".format(strike, options_month[contract][strike]["open_interest"]))
            except ValueError:
                pass
        print("\n")


def main(symbol, month):
    (futures, options) = sp.get_all_options(symbol)
    
    futures_month = futures[month]
    # futures_month: expiration date and underlying price
    options_month = options[symbol][month]
    # options month[call_or_put][strike][OI/vol/price/delta/gamma]

    print_OI(options_month)
    sys.exit(0)

    averages = get_average_option(options_month)
    average_call = averages["CALL"]
    average_put = averages["PUT"]
    average_option = averages["TOTAL"]

    step_size = PRODUCT_SYMBOLS[symbol]["step"]
    price_ladder = get_price_ladder(futures_month, averages, step_size)

    skewed_months = make_skewed_months(options_month, futures_month, price_ladder, step_size)

    greek = "delta"
    theo_price = 337.0
    #coefficients = theo_greek_at_price(skewed_months, greek, price_ladder, theo_price)["coefficients"]
    print(theo_greek_at_price(skewed_months, greek, price_ladder, theo_price))
    #print(theo_price_at_greek(coefficients, -120000))


if __name__ == "__main__":

    symbol = sys.argv[1]
    month = sys.argv[2]
    main(symbol, month)
