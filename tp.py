from sp import PRODUCT_SYMBOLS
import wi
import plotter
import os
import sys
import subprocess

MONTH_LETTERS = {'JAN': 'F',
                 'FEB': 'G',
                 'MAR': 'H',
                 'APR': 'J',
                 'MAY': 'K',
                 'JUN': 'M',
                 'JLY': 'N',
                 'AUG': 'Q',
                 'SEP': 'U',
                 'OCT': 'V',
                 'NOV': 'X',
                 'DEC': 'Z'}


def get_tex_template(settlement_date, commodity, months, graphics):
    with open("template.tex", "r") as f:
        template = f.read()

    return template.format(date=settlement_date, commodity=commodity, months=months, graphics=graphics)


def sort_months(options):

    months = []
    for key in options.keys():
        months.append(key)

    months.sort(key=lambda month: MONTH_LETTERS[month[:3]])
    months.sort(key=lambda month: month[-2:])

    return months


def oi_month_line(symbol, month, options):

    month_abbreviation = "{0}{1}".format(MONTH_LETTERS[month[:3]], month[-1])
    average_options = wi.get_average_option(options)
    total_delta = wi.calc_total_greek(options, 'delta')
    sig_figs = PRODUCT_SYMBOLS[symbol]["sig_figs"]

    month_dict = {}

    month_dict["month"] = month
    month_dict["Contract"] = "{0}{1}".format(symbol, month_abbreviation)
    line = month_dict["Contract"]
    for contract in ["CALL", "PUT"]:
        total_oi = 0
        for key in options[contract].keys():
            total_oi += options[contract][key]["open_interest"]
        month_dict["{0}_oi".format(contract)] = total_oi
        line += " & {0:,.0f}".format(total_oi)

    month_dict["CALL_delta"] = total_delta["CALL"]
    month_dict["PUT_delta"] = total_delta["PUT"]
    line += " & {0:,.0f} & {1:,.0f}".format(
        month_dict["CALL_delta"],
        month_dict["PUT_delta"])

    month_dict["avg_CALL"] = average_options["CALL"]
    month_dict["avg_PUT"] = average_options["PUT"]
    month_dict["avg_TOTAL"] = average_options["TOTAL"]   
    if sig_figs == 0:
        line += " & {0} & {1}".format(
            int(round(month_dict["avg_CALL"], sig_figs)),
            int(round(month_dict["avg_PUT"], sig_figs)))
        line += " & {0}".format(
            int(round(month_dict["avg_TOTAL"], sig_figs)))
    else:
        line += " & {0} & {1}".format(
            round(month_dict["avg_CALL"], sig_figs),
            round(month_dict["avg_PUT"], sig_figs))
        line += " & {0}".format(
            round(month_dict["avg_TOTAL"], sig_figs))

    if month == options["underlying"]["name"]:
        line += " & {0} \\\\\n".format(options["underlying"]["open_interest"])
    else:
        line += " & \\\\\n"
  
    return {"tex_string": line, "data": month_dict}


def big_months(options, num_months=3):
    total_oi = {}
    for month in options.keys():
        oi = 0
        for contract in ["CALL", "PUT"]:
            for strike in options[month][contract].keys():
                oi += options[month][contract][strike]["open_interest"]
        total_oi[oi] = month

    oi_list = []
    for oi in total_oi.keys():
        oi_list.append(oi)
    oi_list.sort(reverse=True)

    oi_list = oi_list[:num_months]
    month_list = []
    for oi in oi_list:
        month_list.append(total_oi[oi])
    month_list.sort(key=lambda month: MONTH_LETTERS[month[:3]])
    month_list.sort(key=lambda month: month[-2:])
    
    return month_list


def oi_tex_maker(settlements, symbol, oi=True, graphics=True):
        
    options = settlements["options"]
    months = sort_months(options)
    commodity = PRODUCT_SYMBOLS[symbol]["name"]
    settlement_date = settlements["settlement_date"]
    date_text = settlement_date.strftime("%B %d, %Y")

    months_tex = ""
    month_data = {}
    if oi:
        for month in months:
            month_line = oi_month_line(symbol, month, options[month])
            months_tex += month_line["tex_string"]

            month_data[month_line["data"]["month"]] = month_line["data"]

        months_tex += "\\hline\n"

    graphics_tex = ""
    if graphics:
        for month in big_months(options):
            imgs = plotter.make_all(settlements, symbol, month)
            for img in imgs:
                graphics_tex += "\n\\newpage\n\\includegraphics"
                graphics_tex += "{{{0}}}".format(img[:-4]) # Removes the file extension
                
    tex = get_tex_template(date_text, commodity, months_tex, graphics_tex)
        
    tex_to_pdf(tex, symbol, settlement_date)

    return month_data


def tex_to_pdf(tex, symbol, settlement_date):

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, "reports")
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    file_name = settlement_date.strftime("%m_%d_%Y")
    file_name += "_{0}".format(symbol)

    with open("{0}".format(os.path.join(script_dir, "{0}.tex".format(file_name))),
              "w") as f:
        f.write(tex)

    subprocess.call("latex --output-format=pdf {0}".format(os.path.join(script_dir, "{0}.tex".format(file_name))),
                    shell=True)
    subprocess.call("mv {0}.pdf reports".format(file_name), shell=True)
    subprocess.call("rm {0}.tex".format(file_name), shell=True)

    for root, dirs, files in os.walk(script_dir):
        for currentFile in files:
            exts = (".aux", ".log")
            if any(currentFile.lower().endswith(ext) for ext in exts):
                os.remove(os.path.join(root, currentFile))

    #subprocess.call("echo \"{0} Options Open Interest\" | mail -s \"{0} Options\" -A ~/settlement-parser/reports/{1}.pdf bthrelkeld@rcgdirect.com".format(PRODUCT_SYMBOLS[symbol]["name"], file_name))
    subprocess.call("echo \"{0} Options Open Interest\" | mail -s \"{0} Options\" -A ~/settlement-parser/reports/{1}.pdf chathrel@indiana.edu".format(PRODUCT_SYMBOLS[symbol]["name"], file_name))


def main(symbol):
    
    oi_tex_maker(symbol)

    
if __name__ == '__main__':
    symbols = sys.argv[1:]
    for symbol in symbols:
        main(symbol)
