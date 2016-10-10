import datetime
import os
import urllib.request
import numpy
from scipy import optimize, stats
import sys

PRODUCT_SYMBOLS = {"S": {"name": "soybeans",
                         "futures": "S Soybean Futures",
                         "options": "SOYBEANS OPTION",
                         "strike_divisor": 10,
                         "has short-dated": True,
                         "short-dated": "Short-Dated New Crop Soybean Option",
                         "tick_size": 0.125},
                   "C": {"name": "corn",
                         "futures": "C Corn Future",
                         "options": "Corn Options",
                         "strike_divisor": 10,
                         "has short-dated": True,
                         "short-dated": "Short-Dated New Crop Corn Option",
                         "tick_size": 0.125},
                    "W": {"name": "wheat",
                          "futures": "W Wheat Futures",
                          "options": "Wheat Options",
                          "strike_divisor": 10,
                          "has short-dated":True,
                          "short-dated": "Short-Dated New Crop Wheat Option",
                          "tick_size": 0.125},
                    "KC": {"name": "kansas city wheat",
                           "futures": "KEF Kansas City Wheat Futures",
                           "options": "Kansas City Wheat Options",
                           "strike_divisor": 10,
                           "has short-dated": False,
                           "tick_size": 0.125},
                    "SM": {"name": "soybean meal",
                           "futures": "SM Soybean Meal Futures",
                           "options": "Soybean Meal Options",
                           "strike_divisor": 100,
                           "has short-dated": False},
                    "BO": {"name": "soybean oil",
                           "futures": "BO Soybean Oil Futures",
                           "options": "Soybean Oil Options",
                           "strike_divisor": 1000,
                           "has short-dated": False}
                   }
INTEREST_RATE = 0.01
TESTING = False


def get_settlements():
    """
    Retrieve 6:00PM settlements from the CME website.
    Saves to a file named file_name.
    """

    i = datetime.datetime.now()

    if not (i.hour > 14 or (i.hour > 13 and i. minute > 29)):
        while True:
            i -= datetime.timedelta(days=1)
            if i.weekday() < 5:
                break

    file_name = "{0}_{1}_{2}_settlements.txt".format(i.day, i.month, i.year)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, "Settlements")
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    file_path = os.path.join(dest_dir, file_name)

    if not os.path.isfile(file_path):
        url = "ftp://ftp.cmegroup.com/pub/settle/stlags"
        urllib.request.urlretrieve(url, file_path)
    return {"file_name": file_name, "directory": dest_dir}


def make_expiration_dict():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.join(script_dir, "expiration_dates.csv")

    expiration_dict = {}

    with open(file_name, "r") as dates:
        while True:
            theline= dates.readline().split(",")
            try:
                contract = theline[0]
                month = int(theline[1])
                day = int(theline[2])
                year = int(theline[3])
                expiration_dict[contract] = datetime.date(year=year, month=month, day=day)
            except IndexError:
                break

    return expiration_dict


def isolate_commodity(settles, symbol):
    """
    Retrieves only the settlements of the given commodity from the settle file
    Saves these settlements in a new file.
    """

    file_name = "{0}_{1}".format(PRODUCT_SYMBOLS[symbol]["name"], settles["file_name"])
    all_settles = os.path.join(settles["directory"], settles["file_name"])
    comm_file = os.path.join(settles["directory"], file_name)

    if not os.path.isfile(comm_file):
        on = False
        output = ""
        settlements = open(all_settles, "r")

        with open(all_settles, "r") as settlements:
            while True:
                theline = settlements.readline()

                if len(theline) == 0:
                    break
                if PRODUCT_SYMBOLS[symbol]["futures"] in theline:
                    on = True
                if PRODUCT_SYMBOLS[symbol]["options"] in theline:
                    on = True
                if PRODUCT_SYMBOLS[symbol]["has short-dated"]:
                    if PRODUCT_SYMBOLS[symbol]["short-dated"] in theline:
                        on = True

                if on and "EST.VOL" in theline:
                    output += "\n"
                    on = False
                if on and ("Minneapolis" in theline or "Kansas City" in theline or "Mini-Sized" in theline):
                    if not symbol == "KC":
                        on = False

                if on:
                    output += theline

        with open(comm_file, "w") as symbol_settles:
            symbol_settles.write(output)

    return {"file_name": comm_file, "directory": settles["directory"]}


def ticks_to_decimal(ticks, symbol):

    if "'" in ticks:
        try:
            cents = float(ticks.split("'")[0])
        except ValueError:
            cents = 0
        fraction = float(ticks.split("'")[1])
        return cents + fraction * PRODUCT_SYMBOLS[symbol]["tick_size"]
    else:
        return float(ticks)


def make_futures_dict(settles, symbol, expiration_dict):

    file_name = os.path.join(settles["directory"], settles["file_name"])
    futures_dict = {}

    with open(file_name, "r") as settlements:
        on = False

        while True:
            theline = settlements.readline()

            if on:
                l = theline.split()
                try:
                    contract = l[0]
                except IndexError:
                    on = False
                    break

                ticks = l[5]
                try:
                    settlement = ticks_to_decimal(ticks, symbol)
                except ValueError:
                    print(theline)
                    sys.exit(0)
                try:
                    expiration = expiration_dict[contract]
                    futures_dict[contract] = {"price": settlement,
                                              "expiration": expiration}
                except KeyError:
                    pass

            if PRODUCT_SYMBOLS[symbol]["futures"] in theline:
                on = True

    return futures_dict


def calc_call_greeks(S, K, T, D1):
    delta = 0
    if T <= 0:
        if K < S:
            return 1
        else:
            return 0
    greeks = {}
    greeks["delta"] = stats.norm.cdf(D1)
    return greeks


def calc_put_greeks(S, K, T, D1):
    delta = 0
    greeks = {}

    if T <= 0:
        if K > S:
            return 1
        else:
            return 0

    greeks["delta"] = -1 * stats.norm.cdf(-D1)
    return greeks


def calc_gamma(v, S, T, D1):
    gamma = stats.norm.pdf(D1) / (S * v * numpy.sqrt(T))
    return gamma


def calc_vanna(v, D1, D2):
    vanna = (stats.norm.pdf(D1) * D2) / v
    return vanna


def calc_vega(S, D1, T):
    vega = S * stats.norm.pdf(D1) * numpy.sqrt(T)
    return vega


def make_strike_dict(S, K, T, sett, call_or_put, r=INTEREST_RATE,):
    try:
        vol = optimize.brentq(theo_BS_diff, 0.0, 2.0, args=(sett, S, K, T, r, call_or_put))
    except:
        vol = 0.1
    D1 = d1(vol, S, K, T)
    D2 = d2(vol, S, K, T)
    if call_or_put == "CALL":
        greeks = calc_call_greeks(S, K, T, D1)
    if call_or_put == "PUT":
        greeks = calc_put_greeks(S, K, T, D1)
    greeks["gamma"] = calc_gamma(vol, S, T, D1)
    greeks["vega"] = calc_vega(S, D1, T)
    greeks["vanna"] = calc_vanna(vol, D1, D2)
    greeks["volatility"] = vol

    return greeks


def black_scholes(v, S, K, T, r=INTEREST_RATE):
    """
        Returns the value of a call using the Black-Scholes model.
        S = Price of underlying
        t = years until expiration
        K = Strike price
        V = annual volatility
        r = interest rate
    """
    D1 = d1(v, S, K, T, r)
    D2 = d2(v, S, K, T, r)
    val = S * stats.norm.cdf(D1) - K * numpy.exp(-r*T) * stats.norm.cdf(D2)
    return val


def put_call_parity(v, S, K, T, r=INTEREST_RATE):
    """
        Uses put-call parity to calculate the value of a put option.
    """
    C = black_scholes(v, S, K, T, r)
    put = numpy.exp(-r*T) * K + C - S
    return put


def theo_BS_diff(x, sett, S, K, T, r=INTEREST_RATE, cac="CALL"):
    if cac == "CALL":
        diff = sett - black_scholes(x, S, K, T, r)
    else:
        diff = sett - put_call_parity(x, S, K, T, r)
    return diff


def d1(v, S, K, T, r=INTEREST_RATE):
    D1 = (numpy.log(S/K) + (r + v*v/2)*T) / (v * numpy.sqrt(T))
    return D1


def d2(v, S, K, T, r=INTEREST_RATE):
    D2 = (numpy.log(S/K) + (r - v*v/2)*T) / (v * numpy.sqrt(T))
    return D2


def make_options_dict(settles, symbol, futures_dict, month):

    file_name = os.path.join(settles["directory"], settles["file_name"])
    options_dict = {"CALL": {}, "PUT": {}}
    today = datetime.date.today()

    with open(file_name, "r") as settlements:
        on = False
        call_or_put = ""    # will be "CALL" or "PUT"
        S = futures_dict[month]["price"]
        T = float((futures_dict[month]["expiration"] - today).days) / 365
        prev_line = ";lakjsdf"

        while True:
            theline = settlements.readline()
            if prev_line == theline:
                break
            prev_line = theline
            if on:
                try:
                    strike = int(theline.split()[0]) / PRODUCT_SYMBOLS[symbol]["strike_divisor"]
                except(ValueError, IndexError):
                    on = False
                    continue
                else:
                    settle = ticks_to_decimal(theline.split()[5], symbol)

                    greeks = make_strike_dict(S=S,
                                              K=strike,
                                              T=T,
                                              sett=settle,
                                              call_or_put=call_or_put
                                              )

                    if "'" in theline.split()[-1]:
                        open_interest = 0
                    else:
                        try:
                            open_interest = int(theline.split()[-1])
                        except ValueError:
                            open_interest = 0

                    options_dict[call_or_put][strike] = greeks
                    options_dict[call_or_put][strike]["open_interest"] = open_interest
                    options_dict[call_or_put][strike]["price"] = settle


            if PRODUCT_SYMBOLS[symbol]["options"] in theline:
                try:
                    if month == theline.split()[1]:
                        call_or_put = theline.split()[-1]
                        on = True
                except KeyError:
                    pass

    return options_dict


def get_all_options(symbol):
    
    if TESTING:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dest_dir = os.path.join(script_dir, "Settlements")
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)
        file_name = "27_9_2016_settlements.txt"
        settlements = {"file_name": file_name, "directory": dest_dir}
    else:
        settlements = get_settlements()

    expiration_dict = make_expiration_dict()
    settlements = isolate_commodity(settlements, symbol)
    futures = make_futures_dict(settlements, symbol, expiration_dict)

    options = {}
    for key in futures.keys():
        options[key] = make_options_dict(settlements,
                                              symbol,
                                              futures,
                                              key)

    return (futures, options)


def main(symbol, month):
    (futures, options) = get_all_options(symbol)

    output = "strike,price,delta,vol,open interest,gamma\n"
    for i in ["CALL", "PUT"]:
        output += "{0},{1}\n".format(month, i)
        strikes = []
        for key in options[symbol][month][i].keys():
            strikes.append(key)

        strikes.sort()

        for strike in strikes:
            output += "{0},{1},{2},{3},{4},{5}\n".format(strike,
                                                   options[symbol][month][i][strike]["price"],
                                                   options[symbol][month][i][strike]["volatility"],
                                                   options[symbol][month][i][strike]["open_interest"],
                                                   options[symbol][month][i][strike]["delta"],
                                                   options[symbol][month][i][strike]["gamma"]
                                                   )
    today = datetime.date.today()
    with open("{0}_{1}_as_of_{2}_{3}.csv".format(symbol, month, today.month, today.day), "w") as file:
            file.write(output)


if __name__ == '__main__':

    symbol = sys.argv[1]
    month = sys.argv[2]
    main(symbol, month)