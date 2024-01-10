from model import (Base, session, Product, engine)
import datetime
import csv
import time

def menu():
    while True:
        print('''----------------------------------------------------
        \nStore Inventory
        \rView a product (v)
        \rAdd new product to database (a)
        \rBackup the data from database (b)
        \rExit from the inventory (q)
-----------------------------------------------------''')
        choice = input('What would you like to do?')
        if choice in ['a', 'v', 'b', 'q']:
            return choice
        else:
            input('''
            \r Please choose one of the options above
            \rAny of the options from 'v', 'a', 'b', 'q'
            \r Press enter to try again...''')


def clean_price(price):
    try:
        modified_price = int(float(price[1:]) * 100)
    except ValueError:
        input('''
                \n ***** Price Error *****
                \r The price format should be a valid number without currency
                \r Ex: 35.96
                \r Press enter to try again ...
                \r*************************)
                ''')
        return
    else:
        return modified_price


def clean_quantity(qty):
    try:
        modified_qty = int(qty)
    except ValueError:
        input('''
                    \n ***** Quantity Error *****
                    \r The quantity should be a valid number
                    \r Ex: 3
                    \r Press enter to try again ...
                    \r*************************)''')
        return
    else:
        return modified_qty


def clean_date(updated_date_str):
    try:
        split_date = updated_date_str.split("/")
        month = int(split_date[0])
        day = int(split_date[1])
        year = int(split_date[2])
        modified_date = datetime.date(year, month, day)
    except (ValueError, IndexError):
        input('''
        \n ***** Date Error *****
        \r The date format should include a valid Month, Day and Year from the past
        \r Ex: 4/15/2018
        \r Press enter to try again ...
        \r*************************)''')
        return
    else:
        return modified_date


def clean_product_id(product_id, available_id):
    try:
        modified_id = int(product_id)
    except ValueError:
        input('''
                \n ***** ID Error *****
                \r Id should be a digit
                \r Ex: 1 
                \r Press enter to try again ...''')
        return
    else:
        if modified_id in available_id:
            return modified_id
        else:
            input('''
            \nThere is no product with that id
            \rPlease enter an id present within the given options
            \rPress enter to try again...''')
            return


def add_csv():
    with open("inventory.csv") as csvfile:
        data = csv.reader(csvfile)
        next(data)
        for row in data:

            existing_product = session.query(Product).filter(Product.product_name == row[0]).one_or_none()
            if existing_product is not None:
                if clean_date(row[3]) > existing_product.date_updated:
                    existing_product.product_price = clean_price(row[1])
                    existing_product.product_quantity = clean_quantity(row[2])
                    existing_product.date_updated = clean_date(row[3])
                else:
                    continue
            else:
                product_name = row[0]
                product_price = clean_price(row[1])
                product_quantity = clean_quantity(row[2])
                date_updated = clean_date(row[3])
                new_product = Product(product_name=product_name, product_price=product_price, product_quantity=product_quantity, date_updated=date_updated)
                session.add(new_product)
        session.commit()


def app():
    app_running = True
    while app_running:
        user_choice = menu()
        if user_choice == 'v':
            available_id_options = []
            for product in session.query(Product):
                available_id_options.append(product.product_id)
            id_error = True
            while id_error:
                id_choice = clean_product_id(input(f'''
                                \n Id Options: {available_id_options}
                                \r Product Id: '''), available_id_options)
                if type(id_choice) == int:
                    id_error = False
            chosen_product = session.query(Product).filter(Product.product_id == id_choice).first()
            print(f'''
            \n*****************************************************
            \nProduct Details
            \r Product_name: {chosen_product.product_name}
            \r Product_price: {chosen_product.product_price/100}
            \r Product_Quantity: {chosen_product.product_quantity}
            \r Date_updated: {chosen_product.date_updated}
            \n******************************************************''')
        elif user_choice == 'a':
            invalid_name = True
            while invalid_name:
                product_name = input("Product Name: ")
                try:
                    if len(product_name) > 1:
                        invalid_name = False
                    else:
                        raise ValueError
                except ValueError:
                    input('''
                    \nProduct name must not be empty
                    \rPress Enter to try again...''')
            price_error = True
            while price_error:
                product_price = clean_price(input("Price: "))
                if type(product_price) == int:
                    price_error = False
            qty_error = True
            while qty_error:
                qty = clean_quantity(input("Quantity: "))
                if type(qty) == int:
                    qty_error = False
            date_error = True
            while date_error:
                date_updated = clean_date(input("Date Updated Eg(3/7/2018): "))
                if type(date_updated) == datetime.date:
                    date_error = False
            existing_product = session.query(Product).filter(Product.product_name == product_name).one_or_none()
            if existing_product is not None and date_updated > existing_product.date_updated:
                existing_product.product_price = product_price
                existing_product.product_quantity = qty
                existing_product.date_updated = date_updated
            else:
                new_product = Product(product_name=product_name, product_price=product_price, product_quantity=qty, date_updated=date_updated )
                session.add(new_product)
            session.commit()
            print("Product is added")
            time.sleep(1.5)
        elif user_choice == 'b':
            with open('backup.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['product_name', 'product_price', 'product_quantity', 'date_updated'])
                for row in session.query(Product):
                    formatted_date = row.date_updated.strftime("%m/%d/%Y")
                    writer.writerow([row.product_name, f'${row.product_price/100}', row.product_quantity, formatted_date])
            print("Backup is successfully completed!!!")
        elif user_choice == 'q':
            print("Thank you for visiting the Store Inventory application")
            app_running = False


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_csv()
    app()