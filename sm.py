import sp
from sp import PRODUCT_SYMBOLS
import wi
import subprocess
import sys
import os
import tp

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


def daily_change(contract, delta_today, dte):

    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, "OI History")
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    path = os.path.join(dest_dir, contract)

    last_date = 0

    change = "---"

    if os.path.exists(path):
        with open(path, "r") as OI_hist:
            while True:
                theline = OI_hist.readline()
                if len(theline) == 0:
                    break
                try:
                    line_date = int(theline.split()[0])
                    if not line_date == dte:
                        last_delta = int(theline.split()[1])
                        change = int(delta_today - last_delta)
                    last_date = line_date
                except IndexError:
                	pass

    if not last_date == dte:
        with open(path, "a") as OI_hist:
            if os.path.exists(path):
                OI_hist.write("\n{0}\t{1}".format(dte, int(delta_today)))
            else:
                OI_hist.write("{0}\t{1}".format(dte, int(delta_today)))

    return change


def oi_tex_line(settlements, symbol, month):

	month_abbreviation = MONTH_LETTERS[month[:3]]
	single_digit_year = month[4]
	contract = "{0}{1}{2}".format(symbol, month_abbreviation, single_digit_year)

	delta_dict = wi.calc_total_greek(settlements["options"][month], "delta")
	delta_equivalent = delta_dict["CALL"] + delta_dict["PUT"]

	dte = (settlements["options"][month]["expiration_date"] - settlements["settlement_date"]).days
	change = daily_change(contract, delta_equivalent, dte)

	average_options = wi.get_average_option(settlements["options"][month])
	avg_call = average_options["CALL"]
	avg_put = average_options["PUT"]
	avg_option = average_options["TOTAL"]

	price = settlements["options"][month]["underlying"]["price"]
	und_price = sp.decimal_to_ticks(price, symbol)

	if type(change) == type(""):
		tex_line = "{0} & {1:,.0f} & {2}".format(contract,
											  	 delta_equivalent,
												 change)
	else:
		tex_line = "{0} & {1:,.0f} & {2:+,.0f}".format(contract,
												  	   delta_equivalent,
												  	   change)

	sig_figs = PRODUCT_SYMBOLS[symbol]["sig_figs"]
	if sig_figs == 0:
		tex_line += " & {0} & {1} & {2} & {3} \\\\\n".format(
			int(round(avg_call, sig_figs)),
			int(round(avg_put, sig_figs)),
			int(round(avg_option, sig_figs)),
			#und_price)
			round(und_price, sig_figs+1))
	else:
		tex_line += " & {0} & {1} & {2} & {3} \\\\\n".format(
			round(avg_call, sig_figs),
			round(avg_put, sig_figs),
			round(avg_option, sig_figs),
			#und_price)
			round(und_price, sig_figs+1))

	return tex_line


def get_tex_template(settlement_date, option_tex):

	with open("simple_template.tex", "r") as f:
		template = f.read()

	return template.format(date=settlement_date.strftime("%B %d, %Y"), options=option_tex)


def tex_to_pdf(tex, settlement_date):

	script_dir = os.path.dirname(os.path.abspath(__file__))
	dest_dir = os.path.join(script_dir, "options")
	if not os.path.exists(dest_dir):
		os.mkdir(dest_dir)

	file_name = "OOI_{0}".format(settlement_date.strftime("%m_%d_%Y"))

        #HACK
        with open("filename.var") as f:
            f.write(file_name))

	with open("{0}".format(os.path.join(script_dir, "{0}.tex".format(file_name))), "w") as f:
		f.write(tex)

	subprocess.call("pdflatex {0}".format(os.path.join(script_dir, "{0}.tex".format(file_name))), shell=True)
	subprocess.call("mv {0}.pdf options".format(file_name), shell=True)
	subprocess.call("rm {0}.tex".format(file_name), shell=True)

	for root, dirs, files in os.walk(script_dir):
		for currentFile in files:
			exts = (".aux", ".log")
			if any(currentFile.lower().endswith(ext) for ext in exts):
				os.remove(os.path.join(root, currentFile))


def oi_tex_maker(settlements, symbols):

	settlement_date = settlements[symbols[0]]["settlement_date"]

	option_tex = ""

	for symbol in symbols:
		big_months = tp.big_months(settlements[symbol]["options"], 4)
		for month in big_months:
			option_tex += oi_tex_line(settlements[symbol], symbol, month)
		option_tex += "\\hline\n"

	tex = get_tex_template(settlement_date, option_tex)

	tex_to_pdf(tex, settlement_date)


def main(symbols):

	settlements = {}
	for symbol in symbols:
		settlements[symbol] = sp.get_all_settlements(symbol)
	oi_tex_maker(settlements, symbols)


if __name__ == '__main__':

	symbols = sys.argv[1:]
	main(symbols)
