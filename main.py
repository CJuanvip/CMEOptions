import sp
import tp
import odb
import sys


def process(symbol):
    settlements = sp.get_all_settlements(symbol)
    print("{0} settlements gotten".format(sp.PRODUCT_SYMBOLS[symbol]["name"]))
    options_data = tp.oi_tex_maker(settlements, symbol)
    print("tex_made")
    odb.add_data(symbol, settlements, options_data)


def main(args):
        
    if len(args) == 0:
        ps = sp.PRODUCT_SYMBOLS
        for symbol in ps.keys():
            print("{0}\t- {1}".format(symbol, ps[symbol]["name"]))
        symbol = input("\nWhich commodity would you like to analyze? ")
        process(symbol)
    else:
        for arg in args:
            try:
                process(arg)
            except KeyError:
                print("Invalid Product")
                

if __name__ == '__main__':

    main(sys.argv[1:])
