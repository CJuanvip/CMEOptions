import sp
import tp
import odb
import sys


def main(symbol):
	settlements = sp.get_all_settlements(symbol)
	print("settlements gotten")
	options_data = tp.oi_tex_maker(settlements, symbol)
	print("tex_made")
	odb.add_data(symbol, settlements, options_data)


if __name__ == '__main__':
    ps = sp.PRODUCT_SYMBOLS

    for symbol in ps.keys():
        print("{0}\t- {1}".format(symbol, ps[symbol]['name']))

    symbol = input('\nWhich commmodity would you like to analyze?  ')

#    try:
    main(symbol)
    #except KeyError:
    #	print("Invalid Product")
    #	sys.exit(1)
