import sp
import wi
import subprocess
import sys


def option_greek_svg(settlements, symbol, month, greek):

    skewed_months = wi.make_skewed_months(settlements, symbol, month)

    r_price = "price <- c("
    r_calls = "calls <- c("
    r_puts = "puts <- c("

    sorted_keys = []
    for price in skewed_months.keys():
        sorted_keys.append(price)
    sorted_keys.sort()

    for key in sorted_keys:
        r_price += "{0},".format(key)
        greeks = wi.calc_total_greek(skewed_months[key], greek)
        r_calls += "{0},".format(greeks["CALL"])
        r_puts += "{0},".format(greeks["PUT"])

    r_script = 'svg("{0}_{1}_{2}.svg")\n'.format(symbol, month, greek)
    for string in [r_price, r_calls, r_puts]:
        r_script += string[:-1]
        r_script += ")\n"

    r_script += """y_min <- min(c(calls,puts))\n
                   y_max <- max(c(calls,puts,calls+puts))\n
                   plot(c(min(price),max(price)), c(y_min,y_max),
                        type="n",xlab="Price",ylab="{0}",
                        main="{1} {2} Option Market Total {0}")\n
                   lines(price,calls,col="red")\n
                   lines(price,puts,col="darkblue")\n
                   lines(price,calls+puts,col="purple")\n
                   legend("bottom",
                          legend=c("Call {0}","Put {0}","Total {0}"),
                          bty="n",fill=c("red","darkblue","purple"),
                          horiz=TRUE)\n
                   dev.off()""".format(greek, month,
                                       sp.PRODUCT_SYMBOLS[symbol]["name"])

    with open("greek.R", "w") as f:
        f.write(r_script)

    subprocess.call("R -f greek.R", shell=False)


def stacked_options_svg(settlements, symbol, month):

    itm_options = wi.get_itm_ladder(settlements, symbol, month)
    r_price = "price <- c("
    r_calls = "calls <- c("
    r_puts = "puts <- c("

    sorted_keys = []
    for key in itm_options.keys():
        sorted_keys.append(key)
    sorted_keys.sort()

    for key in sorted_keys:
        r_price += "{0},".format(key)
        r_calls += "{0},".format(itm_options[key]["CALL"])
        r_puts += "{0},".format(itm_options[key]["PUT"])

    r_script = 'svg("{0}_{1}_stack.svg")\n'.format(symbol, month)
    for string in [r_price, r_calls, r_puts]:
        r_script += string[:-1]
        r_script += ")\n"

    r_script += """m <- matrix(c(price,calls,puts),nrow=3,byrow=T)\n
                   barplot(m[2:3,],
                           col=c("darkblue","red"),
                           xlab="Price",
                           ylab="Contracts",
                           names=m[1,],
                           cex.axis=0.8,
                           las=2,
                           main="{0} {1} in the Money Options")\n
                   legend("top",legend=c("ITM Calls","ITM Puts"),
                          bty="n",fill=c("darkblue","red"))\n
                   dev.off()""".format(month,
                                       sp.PRODUCT_SYMBOLS[symbol]["name"])
                                   
    with open("stack.R", "w") as f:
        f.write(r_script)

    subprocess.call("R -f stack.R", shell=False)
    

def main(symbol, month):
    settlements = sp.get_all_settlements(symbol)
    stacked_options_svg(settlements, symbol, month)
    option_greek_svg(settlements, symbol, month, "delta")
    option_greek_svg(settlements, symbol, month, "gamma")


if __name__ == "__main__":
    symbol = sys.argv[1]
    month = sys.argv[2]
    main(symbol, month)
