import sp
import wi
import subprocess
import sys
import os


def png_setup(dict_arg, symbol, month, chart_var):

    r_price = "price <- c("
    r_calls = "calls <- c("
    r_puts = "puts <- c("

    sorted_keys = []
    for price in dict_arg.keys():
        sorted_keys.append(price)
    sorted_keys.sort()

    for key in sorted_keys:
        r_price += "{0},".format(key)
        r_calls += "{0},".format(dict_arg[key]["CALL"])
        r_puts += "{0},".format(dict_arg[key]["PUT"])

    img_name = "{0}_{1}_{2}.png".format(symbol, month, chart_var)
    r_script = 'png("{0}_{1}_{2}.png")\n'.format(symbol, month, chart_var)
    for string in [r_price, r_calls, r_puts]:
        r_script += string[:-1]
        r_script += ")\n"

    return (r_script, img_name)


def write_png(r_script, img_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    with open("{0}".format(os.path.join(script_dir, "temp.R")), "w") as f:
        f.write(r_script)

    subprocess.call("R -f {0}".format(os.path.join(script_dir, "temp.R")),
                                      shell=True)
                    
    dest_dir = os.path.join(script_dir, "img")
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
                                 
    subprocess.call("mv {0} ./img".format(img_name), shell=True)


def option_greek_png(skewed_months, symbol, month, greek):

    total_greeks_dict = {}
    for key in skewed_months:
        total_greeks_dict[key] = wi.calc_total_greek(skewed_months[key], greek)
        
    (r_script, img_name) = png_setup(total_greeks_dict, symbol, month, greek)
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

    write_png(r_script, img_name)

    return img_name

def stacked_options_png(settlements, symbol, month):

    itm_options = wi.get_itm_ladder(settlements, symbol, month)

    (r_script, img_name) = png_setup(itm_options, symbol, month, "stack")
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

    write_png(r_script, img_name)

    return img_name
    

def make_all(settlements, symbol, month):
    imgs = []
    imgs.append(stacked_options_png(settlements, symbol, month))
    skewed_months = wi.make_skewed_months(settlements, symbol, month)
    imgs.append(option_greek_png(skewed_months, symbol, month, "delta"))
    imgs.append(option_greek_png(skewed_months, symbol, month, "gamma"))

    return imgs
    
    
def main(symbol, month):
    settlements = sp.get_all_settlements(symbol)
    make_all(settlements, symbol, month)


if __name__ == "__main__":
    symbol = sys.argv[1]
    month = sys.argv[2]
    main(symbol, month)
