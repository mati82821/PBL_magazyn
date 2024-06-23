import tkinter as tk
from tkinter import messagebox, ttk, Menu, StringVar
import sqlite3
import re
def initialize_db():
    """
    Initializes database and creates tables
    """
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

class WarehouseApp:
    """
    Main class of program
    """
    def __init__(self, root):
        """
        Intializes main window
        """
        self.root = root
        self.root.title("System Magazynowy")
        self.create_widgets()
        self.populate_product_list()
        self.create_menu()
        root.config(menu=self.menubar)

    def create_menu(self):
        """
         Creates menu bar
        """
        self.menubar = Menu(root)
        self.menubar.add_cascade(label="Niskie stany magazynowe", command=self.show_critical_tab)
        self.menubar.add_cascade(label="Dostawcy", command=self.show_suppliers_tab)

    def create_widgets(self):
        """
         Creates widgets in apps' main window
        """
        self.product_list = ttk.Treeview(self.root, columns=('ID', 'Name', 'Quantity', 'Description', "Supplier"), show='headings')
        self.product_list.heading('ID', text='ID')
        self.product_list.heading('Name', text='Nazwa')
        self.product_list.heading('Quantity', text='Ilość')
        self.product_list.heading('Description', text='Opis')
        self.product_list.heading('Supplier', text='Dostawca')
        self.product_list.pack(fill=tk.BOTH, expand=True)

        self.search_var = tk.StringVar()
        tk.Label(self.root, text="Wyszukiwanie:").pack(side=tk.LEFT, padx=(10, 0), pady=10)
        tk.Entry(self.root, textvariable=self.search_var).pack(side=tk.LEFT, padx=(0, 10), pady=10)
        self.btn_search = tk.Button(self.root, text="Wyszukaj", command=self.search_product)
        self.btn_search.pack(side=tk.LEFT, padx=(0, 10), pady=10)

        self.btn_increase = tk.Button(self.root, text="+", command=self.increase_quantity)
        self.btn_decrease = tk.Button(self.root, text="-", command=self.decrease_quantity)
        self.btn_add = tk.Button(self.root, text="Dodaj produkt", command=self.add_product)
        self.btn_edit = tk.Button(self.root, text="Edytuj produkt", command=self.edit_product)
        self.btn_delete = tk.Button(self.root, text="Usuń produkt", command=self.delete_product)
        
        self.btn_increase.pack(side=tk.RIGHT, padx=10, pady=10)
        self.btn_decrease.pack(side=tk.RIGHT, padx=10, pady=10)
        self.btn_add.pack(side=tk.RIGHT, padx=10, pady=10)
        self.btn_edit.pack(side=tk.RIGHT, padx=10, pady=10)
        self.btn_delete.pack(side=tk.RIGHT, padx=10, pady=10)

    def populate_product_list(self):
        """
         Populates product list with database entries
        """
        for i in self.product_list.get_children():
            self.product_list.delete(i)
        
        conn = sqlite3.connect('warehouse.db')
        c = conn.cursor()
        c.execute("SELECT id, name FROM suppliers")
        suppliers = c.fetchall()
        suppliers_dict = dict()
        for s in suppliers:
            suppliers_dict.update({s[0] : s[1]})
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        rows = c.fetchall()
        for row in rows:
            self.product_list.insert("", "end", values=(int(row[0]), row[1], int(row[2]), row[3], suppliers_dict.get(row[5])))
        conn.close()

    def add_product(self):
        """
         Shows window to add product
        """
        conn = sqlite3.connect('warehouse.db')
        c = conn.cursor()
        c.execute("SELECT count(*) FROM suppliers")
        number = c.fetchone()
        if number[0] == 0:
            messagebox.showwarning("Ostrzeżenie", "Dodaj dostawcę przed dodawaniem produktu")
        else:
            self.product_form()

    def edit_product(self):
        """
         Shows window to edit product
        """
        selected_item = self.product_list.selection()
        if selected_item:
            item = self.product_list.item(selected_item)
            product_id = item['values'][0]
            self.product_form(product_id)
        else:
            messagebox.showwarning("Ostrzeżenie", "Prosze wybrać produkt który chcesz edytować")

    def delete_product(self):
        """
         Deletes product
        """
        selected_item = self.product_list.selection()
        if selected_item:
            item = self.product_list.item(selected_item)
            product_id = item['values'][0]
            
            conn = sqlite3.connect('warehouse.db')
            c = conn.cursor()
            c.execute("DELETE FROM products WHERE id=?", (product_id,))
            conn.commit()
            conn.close()
            
            self.populate_product_list()
        else:
            messagebox.showwarning("Ostrzeżenie", "Prosze wybrać produkt który chcesz usunąć")

    def product_form(self, product_id=None):
        """
        Creates form to add/edit product
        
        :param product_id: ID of product (used only during editing)
        """
        form = tk.Toplevel(self.root)
        form.title("Produkt")
        
        tk.Label(form, text="Nazwa").grid(row=0, column=0)
        tk.Label(form, text="Ilość").grid(row=1, column=0)
        tk.Label(form, text="Opis").grid(row=2, column=0)
        tk.Label(form, text="Poziom alarmowy stanu mag.").grid(row=3, column=0)
        tk.Label(form, text="Dostawca").grid(row=4, column=0)

        name_entry = tk.Entry(form)
        quantity_entry = tk.Entry(form)
        description_entry = tk.Entry(form)
        critical_point_entry = tk.Entry(form)
        supplier_id_value = StringVar()
        conn = sqlite3.connect('warehouse.db')
        c = conn.cursor()
        c.execute("SELECT id, name FROM suppliers")
        suppliers = c.fetchall()
        supparray = []
        for s in suppliers:
            supparray.append(str("{}: {}").format(s[0],s[1]))
        conn.close()
        supplier_dropdown = tk.OptionMenu(form, supplier_id_value, *supparray)

        name_entry.grid(row=0, column=1)
        quantity_entry.grid(row=1, column=1)
        description_entry.grid(row=2, column=1)
        critical_point_entry.grid(row=3, column=1)
        supplier_dropdown.grid(row=4, column=1)

        if product_id:
            conn = sqlite3.connect('warehouse.db')
            c = conn.cursor()
            c.execute("SELECT * FROM products WHERE id=?", (product_id,))
            product = c.fetchone()
            conn.close()
            
            name_entry.insert(0, product[1])
            quantity_entry.insert(0, product[2])
            description_entry.insert(0, product[3])
            critical_point_entry.insert(0, product[4])
            supplier_id_value.set(supparray[product[5]-1])

        def save_product():
            """
             Performs form data validation and then saves product.
            """
            name = name_entry.get()
            quantity = quantity_entry.get()
            if quantity.isdigit() == False or int(quantity) < 0:
                messagebox.showwarning("Ostrzeżenie", "Ilość musi być liczbą większą lub równą 0")
                form.focus()
                return False
            description = description_entry.get()
            critical_point = critical_point_entry.get()
            if critical_point.isdigit() == False or int(critical_point) < 0:
                messagebox.showwarning("Ostrzeżenie", "Poziom alarmowy musi być liczbą większą lub równą 0")
                form.focus()
                return False
            supplier_id = supplier_id_value.get().split(":")[0]

            conn = sqlite3.connect('warehouse.db')
            c = conn.cursor()
            if product_id:
                c.execute("UPDATE products SET name=?, quantity=?, description=?, criticalPoint=?, supplierId=? WHERE id=?", (name, quantity, description, critical_point, supplier_id, product_id))
            else:
                c.execute("INSERT INTO products (name, quantity, description, criticalPoint, supplierId) VALUES (?, ?, ?, ?, ?)", (name, quantity, description, critical_point, supplier_id))
            conn.commit()
            conn.close()
            if product_id:
                self.critical_point_check(product_id)
            form.destroy()
            self.populate_product_list()

        tk.Button(form, text="Zapisz", command=save_product).grid(row=5, column=0, columnspan=2)

    def search_product(self):
            """
             Searches product using text from search bar.
            """
            search_text = self.search_var.get()
            
            for i in self.product_list.get_children():
                self.product_list.delete(i)
            
            conn = sqlite3.connect('warehouse.db')
            c = conn.cursor()
            c.execute("SELECT id, name FROM suppliers")
            suppliers = c.fetchall()
            suppliers_dict = dict()
            for s in suppliers:
                suppliers_dict.update({s[0] : s[1]})
            c = conn.cursor()
            c.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + search_text + '%',))
            rows = c.fetchall()
            for row in rows:
                self.product_list.insert("", "end", values=(int(row[0]), row[1], int(row[2]), row[3], suppliers_dict.get(row[5])))
            conn.close()
    def increase_quantity(self):
        """
         Increases quantity of selected product by 1.
        """
        selected_item = self.product_list.selection()
        if selected_item:
            item = self.product_list.item(selected_item)
            product_id = item['values'][0]
            current_quantity = item['values'][2]
            
            new_quantity = current_quantity + 1
            
            conn = sqlite3.connect('warehouse.db')
            c = conn.cursor()
            c.execute("UPDATE products SET quantity=? WHERE id=?", (new_quantity, product_id))
            conn.commit()
            conn.close()
            
            self.populate_product_list()
            self.reselect_item(product_id)
        else:
            messagebox.showwarning("Ostrzeżenie", "Zaznacz produkt by zwiększyć stan magazynowy")

    def decrease_quantity(self):
        """
         Decreases quantity of selected product by 1.
        """
        selected_item = self.product_list.selection()
        if selected_item:
            item = self.product_list.item(selected_item)
            product_id = item['values'][0]
            current_quantity = item['values'][2]
            
            if current_quantity > 0:
                new_quantity = current_quantity - 1
                
                conn = sqlite3.connect('warehouse.db')
                c = conn.cursor()
                c.execute("UPDATE products SET quantity=? WHERE id=?", (new_quantity, product_id))
                conn.commit()
                conn.close()
                
                self.populate_product_list()
                self.reselect_item(product_id)
                self.critical_point_check(product_id)
            else:
                messagebox.showwarning("Ostrzeżenie", "Stan nie może być mniejszy niż 0")
        else:
            messagebox.showwarning("Ostrzeżenie", "Zaznacz produkt by zmniejszyć stan magazynowy")

    def reselect_item(self, product_id):
        """
         Reselects item on list after operation
        
        :param product_id: ID of product which needs to be reselected.
        """
        for item in self.product_list.get_children():
            if int(self.product_list.item(item, "values")[0]) == int(product_id):
                self.product_list.selection_set(item)
                self.product_list.focus(item)
                break
    def critical_point_check(self, product_id):
        """
         Performs check on alarm point of quantity of the product
        
        :param product_id: ID of product on which check is performed.
        """
        conn = sqlite3.connect('warehouse.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = c.fetchone()
        if int(product[2]) <= int(product[4]):
            messagebox.showwarning("Ostrzeżenie", "STAN MAGAZYNOWY PRODUKTU {} PRZEKROCZYŁ POZIOM ALARMOWY".format(product[1]))
        conn.close()
    
    def show_critical_tab(self):
        """
         Shows window that presents products with quantities lower or equal to critical point.
        """
        inventory_window = tk.Toplevel(self.root)
        inventory_window.title("Niskie stany magazynowe")

        inventory_list = ttk.Treeview(inventory_window, columns=('ID', 'Name', 'Quantity'), show='headings')
        inventory_list.heading('ID', text='ID')
        inventory_list.heading('Name', text='Nazwa')
        inventory_list.heading('Quantity', text='Ilość')
        inventory_list.pack(fill=tk.BOTH, expand=True)

        conn = sqlite3.connect('warehouse.db')
        c = conn.cursor()
        c.execute("SELECT id, name, quantity, criticalPoint FROM products")
        rows = c.fetchall()
        for row in rows:
            if int(row[2]) <= int(row[3]):
                inventory_list.insert("", "end", values=row)
        conn.close()

    def show_suppliers_tab(self):
        """
         Shows suppliers list window.
        """
        suppliers_window = tk.Toplevel(self.root)
        suppliers_window.title("Dostawcy")

        self.suppliers_list = ttk.Treeview(suppliers_window, columns=('ID', 'Name', 'Description', 'Address', "E-mail", "Phone number"), show='headings')
        self.suppliers_list.heading('ID', text='ID')
        self.suppliers_list.heading('Name', text='Nazwa')
        self.suppliers_list.heading('Description', text='Opis')
        self.suppliers_list.heading('Address', text='Adres')
        self.suppliers_list.heading('E-mail', text='E-mail')
        self.suppliers_list.heading('Phone number', text='Numer telefonu')
        self.suppliers_list.pack(fill=tk.BOTH, expand=True)

        btn_addsupp = tk.Button(suppliers_window, text="Dodaj dostawcę", command=self.add_supplier)
        btn_editsupp = tk.Button(suppliers_window, text="Edytuj dostawcę", command=self.edit_supplier)
        btn_deletesupp = tk.Button(suppliers_window, text="Usuń dostawcę", command=self.delete_supplier)

        btn_addsupp.pack(side=tk.LEFT, padx=10, pady=10)
        btn_editsupp.pack(side=tk.LEFT, padx=10, pady=10)
        btn_deletesupp.pack(side=tk.LEFT, padx=10, pady=10)

        self.populate_suppliers_list()

    def populate_suppliers_list(self):
        """
         Populates suppliers list with data from database.
        """
        for i in self.suppliers_list.get_children():
            self.suppliers_list.delete(i)
        conn = sqlite3.connect('warehouse.db')
        c = conn.cursor()
        c.execute("SELECT id, name, address, description, email, phoneNumber FROM suppliers")
        rows = c.fetchall()
        for row in rows:
            self.suppliers_list.insert("", "end", values=row)
        conn.close()
    def supplier_form(self, supplier_id=None):
        """
        Creates form to add/edit supplier

        :param supplier_id: ID of supplier (used only during editing)
        """
        form = tk.Toplevel(self.root)
        form.title("Dostawca")
        
        tk.Label(form, text="Nazwa").grid(row=0, column=0)
        tk.Label(form, text="Adres").grid(row=1, column=0)
        tk.Label(form, text="Opis").grid(row=2, column=0)
        tk.Label(form, text="Email").grid(row=3, column=0)
        tk.Label(form, text="Nr. telefonu").grid(row=4, column=0)

        name_entry = tk.Entry(form)
        address_entry = tk.Entry(form)
        description_entry = tk.Entry(form)
        email_entry = tk.Entry(form)
        phone_entry = tk.Entry(form)

        name_entry.grid(row=0, column=1)
        address_entry.grid(row=1, column=1)
        description_entry.grid(row=2, column=1)
        email_entry.grid(row=3, column=1)
        phone_entry.grid(row=4, column=1)

        if supplier_id:
            conn = sqlite3.connect('warehouse.db')
            c = conn.cursor()
            c.execute("SELECT * FROM suppliers WHERE id=?", (supplier_id,))
            product = c.fetchone()
            conn.close()
            
            name_entry.insert(0, product[1])
            address_entry.insert(0, product[2])
            description_entry.insert(0, product[3])
            email_entry.insert(0, product[4])
            phone_entry.insert(0, product[5])

        def save_supplier():
            """
             Performs form data validation and then saves supplier.
            """
            name = name_entry.get()
            address = address_entry.get()
            description = description_entry.get()
            email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+$")
            email = email_entry.get()
            if not re.fullmatch(email_pattern, email):
                messagebox.showwarning("Ostrzeżenie", "Wprowadź poprawny adres email")
                form.focus()
                return False
            phone_pattern = re.compile(r"^\+[0-9]{0,14}$")
            phone = phone_entry.get()
            if not re.fullmatch(phone_pattern, phone):
                messagebox.showwarning("Ostrzeżenie", "Wprowadź poprawny numer telefonu")
                form.focus()
                return False
            conn = sqlite3.connect('warehouse.db')
            c = conn.cursor()
            if supplier_id:
                c.execute("UPDATE suppliers SET name=?, address=?, description=?, email=?, phoneNumber=? WHERE id=?", (name, address, description, email, phone, supplier_id))
            else:
                c.execute("INSERT INTO suppliers (name, address, description, email, phoneNumber) VALUES (?, ?, ?, ?, ?)", (name, address, description, email, phone))
            conn.commit()
            conn.close()

            form.destroy()
            self.populate_suppliers_list()
        tk.Button(form, text="Zapisz", command=save_supplier).grid(row=5, column=0, columnspan=2)
    def add_supplier(self):
        """
         Shows adding supplier window.
        """
        self.supplier_form()

    def edit_supplier(self):
        """
         Shows editing supplier window.
        """
        selected_item = self.suppliers_list.selection()
        if selected_item:
            item = self.suppliers_list.item(selected_item)
            supplier_id = item['values'][0]
            self.supplier_form(supplier_id)
        else:
            messagebox.showwarning("Ostrzeżenie", "Prosze wybrać dostawcę którego chcesz edytować")

    def delete_supplier(self):
        """
         Checks if user is sure to delete supplier and deletes supplier.
        """
        selected_item = self.suppliers_list.selection()
        if selected_item:
            item = self.suppliers_list.item(selected_item)
            supplier_id = item['values'][0]
            sure = messagebox.askquestion("Usuwanie", "Czy na pewno chcesz usunąć dostawcę {}?".format(item['values'][1]))
            if sure == "yes":
                conn = sqlite3.connect('warehouse.db')
                c = conn.cursor()
                c.execute("SELECT count(*) FROM products WHERE supplierId = ?", (supplier_id,))
                prod_count = c.fetchone()[0]
                if prod_count > 0:
                    messagebox.showerror("Błąd", "Do dostawcy przypisane są produkty! Nie można usunąć dostawcy")
                else:
                    c = conn.cursor()
                    c.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
                    conn.commit()
                    conn.close()
        else:
            messagebox.showwarning("Ostrzeżenie", "Prosze wybrać dostawcę którego chcesz usunąć")
        self.populate_suppliers_list()

if __name__ == "__main__":
    initialize_db()
    root = tk.Tk()
    app = WarehouseApp(root)
    root.mainloop()