import sp
import wi
import sys

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


def make_oi_header(settlement_date):
    header = "%report.text - the python output for tex rendering.\n"
    header += "\\documentclass{article}\n"
    header += "\\usepackage{times}\n"
    header += "\\usepackage[margin=1cm]{geometry}\n"
    header += "\\usepackage{array}\n"
    header += "\\usepackage{caption}\n"
    header += "\\begin{document}\n"
    header += "\\title{Options Open Interest}\n"
    header += "\\date{For Market Date "
    header += settlement_date.strftime("%B %d, %Y")
    header += "}\n"
    header += "\\maketitle\n"
    header += "\\begin{table}[h!]\n"
    header += "\\centering\n"
    header += "\\begin{tabular}{| r | r | r | r | r | r |}\n"
    header += "\\hline\n"
    header += "Contract & Delta Equivalent & Change & Avg Call & Avg Put & Avg Option\n"
    header += "\\\\\n"
    header += "\\hline\n"
    header += "& & & & & \\\\\n"
    header += "\\hline\n"

    return header


def make_oi_footer():
    footer = "\\hline\n"
    footer += "\\end{tabular}\n"
    footer += "\\caption{This table shows "
    footer += "\\newline 1) the futures equivalent open interest in options on a delta weighted basis. "
    footer += "\\newline 2) the simple average open interest for calls, puts, and combined positions.}\n"
    footer += "\\end{table}\n"
    footer += "\\end{document}\n"

    return footer


def sort_months(futures):

    months = []
    for key in futures.keys():
        months.append(key)

    months.sort(key=lambda month: MONTH_LETTERS[month[:3]])
    months.sort(key=lambda month: month[-2:])

    return months


def oi_month_line(symbol, month, options):

    month_abbreviation = MONTH_LETTERS[month[:3]]
    month_abbreviation += month[-1]
    
    average_options = wi.get_average_option(options)
    total_delta = wi.calc_total_greek(options, 'delta')
    
    line = "{0}{1} & {2:,.0f} &   & {3:.0f} & {4:.0f} & {5:.0f}\\\\\n".format(
        symbol,
        month_abbreviation,
        total_delta,
        average_options["CALL"],
        average_options["PUT"],
        average_options["TOTAL"])

    return line


def oi_tex_maker(symbols):

    header = ""

    oi_out = ""
    for symbol in symbols:
        settlements = sp.get_all_settlements(symbol)
        header = make_oi_header(settlements["settlement_date"])
        options = settlements["options"]
        futures = settlements["futures"]
        months = sort_months(futures)
        months = months[:3]
        for month in months:
            month_line = oi_month_line(symbol, month, options[month])
            oi_out += month_line
        oi_out += "\\hline\n"
        
    footer = make_oi_footer()

    print("{0}{1}{2}".format(header, oi_out, footer))


def main():
    oi_tex_maker(['S', 'C', 'W'])

    
if __name__ == '__main__':
    main()
