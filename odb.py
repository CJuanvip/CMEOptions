import sqlite3
import sys
import sp
import wi


def create_table(cursor):

    cursor.execute("""CREATE TABLE History(
                      Symbol TEXT,
                      Month TEXT,
                      Date TEXT,
                      Delta NUMERIC,
                      Avg_Call NUMERIC, 
                      Avg_Put NUMERIC, 
                      Avg_Option NUMERIC, 
                      Price NUMERIC, 
                      Calls_ITM INT, 
                      Calls_OTM INT,
                      Puts_ITM INT,
                      Puts_OTM INT,
                      Futures_Open_Interest INT)""")
    

def add_datum(cursor, table):

    cursor.execute("INSERT INTO History VALUES()".format(table))


def add_data(cursor, table, data):

    execute_command = "INSERT INTO {0} VALUES".format(table)
    execute_command += "(?,?,?,?,?,?,?,?,?,?,?,?,?)"
    cursor.executemany(execute_command, data)
    
    
def main():

    symbols = ['S', 'C', 'W']

    data = []
    for symbol in symbols:
        
        settlements = sp.get_all_settlements(symbol)
        date = settlements["settlement_date"]
        date = date.strftime("%d-%m-%y")
        
        for month in settlements["futures"].keys():
            option_month = settlements["options"][month]
            underlying_price = settlements["futures"][month]["price"]
                
            delta = wi.calc_total_greek(option_month, "delta")
            averages = wi.get_average_option(option_month)
            avg_call = averages["CALL"]
            avg_put = averages["PUT"]
            avg_opt = averages["TOTAL"]
            price = settlements["futures"][month]["price"]
            
            options_count = wi.count_options(option_month, underlying_price)
            calls_itm = options_count["CALL"]["ITM"]
            calls_otm = options_count["CALL"]["OTM"]
            puts_itm = options_count["PUT"]["ITM"]
            puts_otm = options_count["PUT"]["OTM"]

            futures_oi = settlements["futures"][month]["open_interest"]

            data.append((symbol,
                         month,
                         date,
                         delta,
                         avg_call,
                         avg_put,
                         avg_opt,
                         price,
                         calls_itm,
                         calls_otm,
                         puts_itm,
                         puts_otm,
                         futures_oi))

    conn = sqlite3.connect('odb.db')

    with conn:

        cursor = conn.cursor()
        try:
          create_table(cursor)
        except sqlite3.OperationalError:
          pass
        add_data(cursor, "History", data)

if __name__ == '__main__':
    main()
