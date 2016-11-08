import sqlite3
import sys
import sp
import wi


def create_tables(cursor):

    cursor.execute("""CREATE TABLE If NOT EXISTS Futures(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Symbol TEXT,
        Month TEXT,
        Date TEXT,
        Price NUMERIC, 
        Open_Interest INT)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS Options (
        Month TEXT,
        Date TEXT,
        Num_Calls INT,
        Num_Puts INT,
        Delta_Calls NUMERIC,
        Delta_Puts NUMERIC,
        Avg_Call NUMERIC,
        Avg_Put NUMERIC,
        Avg_Total NUMERIC,
        futures_id INTEGER,
        FOREIGN KEY(futures_id) REFERENCES Futures(id))""")    

    
def add_futures_data(cursor, futures_data):

    execute_command = "INSERT INTO Futures Values(NULL,"
    execute_command += "'{0}','{1}','{2}','{3}','{4}')".format(
        futures_data["symbol"],
        futures_data["month"],
        futures_data["date"],
        futures_data["price"],
        futures_data["oi"])
    cursor.execute(execute_command)


def add_options_data(cursor, options_data):

    execute_command = "INSERT INTO Options Values("
    execute_command += "'{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')".format(
        options_data["month"],
        options_data["date"],
        options_data["num_calls"],
        options_data["num_puts"],
        options_data["delta_calls"],
        options_data["delta_puts"],
        options_data["avg_call"],
        options_data["avg_put"],
        options_data["avg_total"],
        options_data["underlying_id"])
    cursor.execute(execute_command)


def get_futures_data(symbol, settlements):

    date = settlements["settlement_date"]
    date = date.strftime("%d-%m-%y")
    
    futures_data = []
    for key in settlements["futures"]:
        datum = {}
        datum["symbol"] = symbol
        datum["month"] = key
        datum["date"] = date
        datum["price"] = settlements["futures"][key]["price"]
        datum["oi"] = settlements["futures"][key]["open_interest"]
        futures_data.append(datum)

    return futures_data
    

def get_options_data(symbol, settlements, options_tp, cursor):

    date = settlements["settlement_date"]
    date = date.strftime("%d-%m-%y")

    options_data = []
    for key in options_tp:
        datum = {}
        underlying_month = sp.match_underlying(key, settlements["futures"])["name"]
        underlying_cursor = cursor.execute('SELECT * FROM Futures WHERE Month = "{0}" AND Date = "{1}"'.format(underlying_month, date))
        underlying = underlying_cursor.fetchone()
        try:
            datum["underlying_id"] = underlying[0]
            datum["month"] = key
            datum["date"] = date
            datum["num_calls"] = options_tp[key]["CALL_oi"]
            datum["num_puts"] = options_tp[key]["PUT_oi"]
            datum["delta_calls"] = options_tp[key]["CALL_delta"]
            datum["delta_puts"] = options_tp[key]["PUT_delta"]
            datum["avg_call"] = options_tp[key]["avg_CALL"]
            datum["avg_put"] = options_tp[key]["avg_PUT"]
            datum["avg_total"] = options_tp[key]["avg_TOTAL"]
            options_data.append(datum)
        except TypeError:
            print("{0} not found in database".format(key))
            print("searched for {0} underlying".format(underlying_month))

    return options_data


def add_data(symbol, settlements, options_tp):

    futures_data = get_futures_data(symbol, settlements)

    date = settlements["settlement_date"].strftime("%d-%m-%y")

    conn = sqlite3.connect("odb.db")

    with sqlite3.connect("odb.db") as conn:
        cur = conn.cursor()
        create_tables(cur)
        
        current = cur.execute('SELECT * FROM Futures WHERE Date="{0}" AND Symbol="{1}"'.format(date, symbol))
        if not current.fetchone():
            for future in futures_data:
                add_futures_data(cur, future)
            conn.commit()

            options_data = get_options_data(symbol, settlements, options_tp, cur)

            for option in options_data:
                add_options_data(cur, option)
            conn.commit()
        else:
            print("Settlements already committed to database")