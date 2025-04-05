import pyodbc
from contextlib import contextmanager

def get_connection():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=PHANI\\PKM01;' ## need to update final server name
        'DATABASE=Expense_Tracker;' 
        'Trusted_Connection=yes;'
    )
    return conn

@contextmanager
def with_connection():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    finally:
        conn.close()