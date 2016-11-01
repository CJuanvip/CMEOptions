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
        r_price += "{0},".format(round(key, 
            sp.PRODUCT_SYMBOLS[symbol]["sig_figs"]))
        r_calls += "{0},".format(dict_arg[key]["CALL"])
        r_puts += "{0},".format(dict_arg[key]["PUT"])

    r_script = ""
    for string in [r_price, r_calls, r_puts]:
        r_script += string[:-1]
        r_script += ")\n"

    img_name = "{0}_{1}_{2}.png".format(symbol, month, chart_var)
    
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

    total_greek_dict = {}
    for key in skewed_months:
        total_greek = wi.calc_total_greek(skewed_months[key], greek)
        total_greek_dict[key] = total_greek

    (args, img_name) = png_setup(total_greek_dict, symbol, month, greek)

    with open("greek_template.R", "r") as f:
        template = f.read()

    r_script = template.format(symbol=symbol,
                               args=args,
                               month=month,
                               greek=greek, 
                               commodity=sp.PRODUCT_SYMBOLS[symbol]["name"])

    write_png(r_script, img_name)

    return img_name


def stacked_options_png(settlements, symbol, month):

    itm_options = wi.get_itm_ladder(settlements, symbol, month)

    (args, img_name) = png_setup(itm_options, symbol, month, "stack")

    with open("stack_template.R", "r") as f:
        template = f.read()

    r_script = template.format(symbol=symbol,
                               args=args,
                               month=month, 
                               commodity=sp.PRODUCT_SYMBOLS[symbol]["name"])
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
    skewed_months = wi.make_skewed_months(settlements, symbol, month)

    make_all(settlements, symbol, month)


if __name__ == "__main__":
    symbol = sys.argv[1]
    month = sys.argv[2]
    main(symbol, month)
