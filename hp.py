import sys
import sp
import os
import subprocess


def main():
    data = []
    with open("CZ6.csv", "r") as f:
        while True:
            l = f.readline().split(",")
            try:
                data.append( {"dte": l[0],
                              "date":l[1],
                              "delta":l[2],
                              "avg_call":l[3],
			      "avg_put": l[4],
			      "avg_opt": l[5],
			      "price": l[6]})
            except IndexError:
                break

    symbol = "C"
    month = "DEC17"
        
    dte = "dte <- c("
    date = "dates <- c("
    delta = "deltas <- c("
    avg_call = "avg_call <- c("
    avg_put = "avg_put <- c("
    avg_option = "avg_opt <- c("
    price = "price <- c("
        
    for datum in data:
        dte += "{0},".format(datum["dte"])
        date += "{0},".format(datum["date"])
        delta += "{0},".format(datum["delta"])
        avg_call += "{0},".format(datum["avg_call"])
        avg_put += "{0},".format(datum["avg_put"])
        avg_option += "{0},".format(datum["avg_opt"])
        price += "{0},".format(datum["price"])

    args = ""
    for v in [dte, date, delta, avg_call, avg_put, avg_option, price]:
        arg = v[:-1]
        arg += ")\n"
        args += arg

    with open("history_template.R", "r") as f:
        template = f.read()

    r_script = template.format(symbol=symbol,
                               args=args,
                               month=month,
                               commodity=sp.PRODUCT_SYMBOLS[symbol]["name"])
	
    script_dir = os.path.dirname(os.path.abspath(__file__))

    with open("{0}".format(os.path.join(script_dir, "temp.R")), "w") as f:
        f.write(r_script)

    #subprocess.call("R -f {0}".format(os.path.join(script_dir, "temp.R")),
                    #shell=True)
                    
    dest_dir = os.path.join(script_dir, "img")
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
                                 
    subprocess.call("mv {0} ./img".format("Hello.png"), shell=True)


if __name__ == '__main__':
    main()
