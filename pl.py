from sp import get_all_settlements, PRODUCT_SYMBOLS
from wi import get_average_option

from matplotlib import pyplot


def get_points(settlements, symbol, month, greek, call_or_put):
    
    xs = []
    for x in settlements['options'][month][call_or_put]:
        xs.append(x)
    xs.sort()
    
    ys = []
    for x in xs:
        ys.append(settlements['options'][month][call_or_put][x][greek])
        
    return (xs, ys)


def get_xmin(avg_put, und_settlement):
    if (und_settlement * 0.9 < avg_put):
        return und_settlement * 0.9
    else:
        return avg_put
    
    
def get_xmax(avg_call, und_settlement):
    if (und_settlement * 1.1 > avg_call):
        return und_settlement * 1.1
    else:
        return avg_call

    
def main(settlements, symbol, month, greek, puts):
    
    settlements = get_all_settlements(symbol)
    
    (call_xs, call_ys) = get_points(settlements, symbol, month, greek, 'CALL')
    pyplot.plot(call_xs, call_ys, marker='x')
    
    if puts:
        (put_xs, put_ys) = get_points(settlements, symbol, month, greek, 'PUT')
        pyplot.plot(put_xs, put_ys, marker='o')
        pyplot.legend(['Calls', 'Puts'])
    
    commodity = PRODUCT_SYMBOLS[symbol]['name']
    pyplot.title('{0} {1} {2}'.format(month, commodity, greek))

    pyplot.xlabel('strikes')
    pyplot.ylabel(greek)
    
    averages = get_average_option(settlements['options'][month])
    und_settlement = settlements['options'][month]['underlying']['price']
    xmin = get_xmin(averages['PUT'], und_settlement)
    xmax = get_xmax(averages['CALL'], und_settlement)
    pyplot.axis(xmin=xmin)
    pyplot.axis(xmax=xmax)
    
    pyplot.savefig("./pollen/{0}/{1}_{2}.png".format(commodity, month, greek))
    pyplot.clf()
    
if __name__ == "__main__":

    settlements = get_all_settlements("S")
    symbol = "S"
    for month in settlements['options'].keys():
        for greek in ['delta', 'gamma', 'vega', 'volatility']:
            if greek  == 'delta':
                puts = True
            else:
                puts = False
            main(settlements, symbol, month, greek, puts)
            
    