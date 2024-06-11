import sqlite3

def initialize_db():
    conn = sqlite3.connect('warehouse.db')
    c = conn.cursor()
    
    # Create products table
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    description TEXT,
                    criticalPoint INTEGER NOT NULL, 
                    supplierId INTEGER NOT NULL)''')

    # Create suppliers table
    c.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    address INTEGER NOT NULL,
                    description TEXT,
                    email TEXT NOT NULL,
                    phoneNumber TEXT NOT NULL)''')
    conn.commit()
    conn.close()

initialize_db()
