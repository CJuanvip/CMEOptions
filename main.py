import sp
import sm
import tp
import odb
import sys


def process(settlements, symbol):
    options_data = tp.oi_tex_maker(settlements, symbol)
    odb.add_data(symbol, settlements, options_data)        

def main(args):

    if len(args) == 0:
        ps = sp.PRODUCT_SYMBOLS
        for symbol in ps.keys():
            print("{0}\t- {1}".format(symbol, ps[symbol]["name"]))
            symbol = input("\nWhich commodity would you like to analyze? ")
            process(symbol)
    else:
        settlements = {}
        for symbol in args:
            try:
                settlements[symbol] = sp.get_all_settlements(symbol)
                process(settlements[symbol], symbol)
            except KeyError:
                print("Invalid Product")
        sm.oi_tex_maker(settlements, args)


if __name__ == '__main__':

    main(sys.argv[1:])
