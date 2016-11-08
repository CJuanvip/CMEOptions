import sp
import tp
import odb
import sys


def main(symbol):
	settlements = sp.get_all_settlements(symbol)
	options_data = tp.oi_tex_maker(settlements, symbol)
	odb.add_data(symbol, settlements, options_data)


if __name__ == '__main__':
    symbols = sys.argv[1:]
    for symbol in symbols:
        main(symbol)