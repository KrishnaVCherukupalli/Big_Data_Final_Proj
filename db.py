import pyodbc

def get_connection():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=PHANI\\PKM01;' ## need to update final server name
        'DATABASE=Expense_Tracker;' 
        'Trusted_Connection=yes;'
    )
    return conn