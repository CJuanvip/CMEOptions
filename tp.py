import sp
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


def make_document_header(settlement_date):
    header = "%report.text - the python output for tex rendering.\n"
    header += "\\documentclass{article}\n"
    header += "\\usepackage{times}\n"
    header += "\\usepackage[margin=1cm]{geometry}\n"
    header += "\\usepackage{array}\n"
    header += "\\usepackage{caption}\n"
    header += "\\usepackage{graphicx}\n"
    header += "\\graphicspath{ {img/} }\n"
    header += "\\begin{document}\n"
    header += "\\title{Options Open Interest}\n"
    header += "\\author{The Lasalle Group}\n"
    header += "\\date{For Market Date "
    header += settlement_date.strftime("%B %d, %Y")
    header += "}\n"

    return header
    

def make_oi_header(symbol):
    header = "\\maketitle\n"
    header += "\\begin{table}[h!]\n"
    header += "\\caption{"
    header += sp.PRODUCT_SYMBOLS[symbol]["name"]
    header += " Options}\n"
    header += "\\centering\n"
    header += "\\begin{tabular}{| r | r | r | r | r | r | r | r |}\n"
    header += "\\hline\n"
    header += "Contract & Num. Calls & Num. Puts & Call Delta & Put Delta & Avg Call & Avg Put & Avg Option\n"
    header += "\\\\\n"
    header += "\\hline\n"
    header += "& & & & & & & \\\\\n"
    header += "\\hline\n"

    return header


def make_oi_footer():
    footer = "\\hline\n"
    footer += "\\end{tabular}\n"
    footer += "\\end{table}\n"

    return footer

    
def make_oi_caption():
    footer = "\\hline\n"
    footer += "\\end{tabular}\n"
    footer += "\\caption*{This table shows "
    footer += "\\newline 1) the number of open options contracts in the market. "
    footer += "\\newline 2) the futures equivalent open interest in options on a delta weighted basis. "
    footer += "\\newline 3) the simple average open interest for calls, puts, and combined positions.}\n"
    footer += "\\end{table}\n"

    return footer
    

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
    sig_figs = sp.PRODUCT_SYMBOLS[symbol]["sig_figs"]

    line = "{0}{1}".format(symbol, month_abbreviation)
    for contract in ["CALL", "PUT"]:
        total_oi = 0
        for key in options[contract].keys():
            total_oi += options[contract][key]["open_interest"]
        line += " & {0:,.0f}".format(total_oi)
    line += " & {0:,.0f} & {1:,.0f}".format(
        total_delta["CALL"],
        total_delta["PUT"])
    line += " & {0} & {1}".format(
        round(average_options["CALL"], sig_figs),
        round(average_options["PUT"], sig_figs))
    line += " & {0} \\\\\n".format(
        round(average_options["TOTAL"], sig_figs))

    return line


def oi_tex_maker(symbols, oi=True, graphics=True):

    oi_out = ""
    graphics = ""
    for symbol in symbols:
        settlements = sp.get_all_settlements(symbol)
        oi_out += make_oi_header(symbol)
        options = settlements["options"]
        futures = settlements["futures"]
        months = sort_months(options)
        for month in months:
            month_line = oi_month_line(symbol, month, options[month])
            oi_out += month_line
        oi_out += "\\hline\n"
        if symbol == symbols[-1]:
            oi_out += make_oi_caption()
        else:
            oi_out += make_oi_footer()

        for month in months[:3]:
            imgs = plotter.make_all(settlements, symbol, month)
            for img in imgs:
                graphics += "\\includegraphics{"
                graphics += img[:-4]
                graphics += "}\n"
                graphics += "\\newpage\n"

    header = make_document_header(settlements["settlement_date"])
        
    footer = make_oi_footer()

    tex = header
    if oi:
        tex += oi_out
    if graphics:
        tex += graphics
    tex += "\\end{document}"
        
    tex_to_pdf(tex, symbols, settlements["settlement_date"])


def tex_to_pdf(tex, symbols, settlement_date):

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, "reports")
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    file_name = settlement_date.strftime("%m_%d_%Y")
    for symbol in symbols:
        file_name += "_{0}".format(symbol)
    
    with open("{0}".format(os.path.join(script_dir, "{0}.tex".format(file_name))),
              "w") as f:
        f.write(tex)

    subprocess.call("latex --output-format=pdf {0}".format(os.path.join(script_dir, "{0}.tex".format(file_name))),
                    shell=True)
    subprocess.call("mv {0}.pdf reports".format(file_name), shell=True)

    for root, dirs, files in os.walk(script_dir):
        for currentFile in files:
            exts = (".tex", ".aux", ".log")
            if any(currentFile.lower().endswith(ext) for ext in exts):
                os.remove(os.path.join(root, currentFile))

def main(symbols):
    
    oi_tex_maker(symbols)

    
if __name__ == '__main__':
    symbols = sys.argv[1:]
    main(symbols)
