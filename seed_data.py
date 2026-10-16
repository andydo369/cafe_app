import sqlite3
import random
from datetime import date, timedelta

import db

# Adds sample data to the database so the app can be tested without typing everything in.
# Run once with: python seed_data.py
# Existing data is kept, new rows are added on top.

ITEMS = [ # (name, price, [(ingredient name, quantity used)])
    ("Classic Milk Tea",        45000, [("Black Tea Leaves", 10), ("Milk", 250)]),
    ("Thai Milk Tea",           50000, [("Thai Tea Mix", 30), ("Milk", 250)]),
    ("Jasmine Green Tea",       35000, [("Green Tea Leaves", 10), ("Sugar Syrup", 30)]),
    ("Oolong Milk Tea",         50000, [("Oolong Tea Leaves", 10), ("Milk", 250)]),
    ("Strawberry Milk Tea",     55000, [("Strawberry Syrup", 40), ("Milk", 250)]),
    ("Mango Fruit Tea",         50000, [("Mango Syrup", 40), ("Green Tea Leaves", 10)]),
    ("Passion Fruit Green Tea", 45000, [("Passion Fruit Syrup", 40), ("Green Tea Leaves", 10)]),
    ("Honeydew Milk Tea",       50000, [("Honeydew Powder", 40), ("Milk", 250)]),
    ("Coffee Milk Tea",         55000, [("Coffee Powder", 20), ("Black Tea Leaves", 10), ("Milk", 250)]),
    ("Lychee Black Tea",        45000, [("Lychee Syrup", 40), ("Black Tea Leaves", 10)]),
]

INGREDIENTS = [ # (name, current_stock, reorder_level)
    ("Black Tea Leaves",    5000,  1000),
    ("Green Tea Leaves",    4000,  1000),
    ("Oolong Tea Leaves",   3000,  1000),
    ("Thai Tea Mix",        6000,  1500),
    ("Strawberry Syrup",    8000,  2000),
    ("Mango Syrup",         1500,  2000), # below reorder level, shows the low stock warning
    ("Passion Fruit Syrup", 7000,  2000),
    ("Honeydew Powder",     5000,  1500),
    ("Coffee Powder",       4000,  1000),
    ("Lychee Syrup",        6500,  2000),
    ("Sugar Syrup",         10000, 3000),
    ("Cheese Foam Mix",     4000,  1000),
    ("Grass Jelly",         6000,  1500),
    ("Pudding",             5000,  1500),
]

SUBCATEGORIES = [ # (name, price, [(ingredient name, quantity used)]), added to every new item
    ("Extra Boba",   5000,  [("Boba", 50)]),
    ("Cheese Foam",  10000, [("Cheese Foam Mix", 30)]),
    ("Grass Jelly",  5000,  [("Grass Jelly", 50)]),
    ("Pudding",      8000,  [("Pudding", 50)]),
    ("Less Sugar",   0,     []),
]

NUMBER_OF_ORDERS = 20


def seed():
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Items WHERE name = ?", (ITEMS[0][0],))
    if cursor.fetchone()[0] > 0: # stops it adding everything twice if run again
        print("Sample data already added, nothing changed.")
        conn.close()
        return

    # Ingredients
    for name, current_stock, reorder_level in INGREDIENTS:
        cursor.execute(
            "INSERT INTO Ingredients (name, current_stock, reorder_level) VALUES (?, ?, ?)",
            (name, current_stock, reorder_level)
        )
    ingredient_ids = dict(cursor.execute("SELECT name, ingredient_id FROM Ingredients").fetchall()) # name -> id

    # Items, their ingredients and their subcategories
    for item_name, item_price, item_ingredients in ITEMS:
        cursor.execute("INSERT INTO Items (name, price) VALUES (?, ?)", (item_name, item_price))
        item_id = cursor.lastrowid
        for ingredient_name, quantity in item_ingredients:
            cursor.execute(
                "INSERT INTO Items_Ingredients (item_id, ingredient_id, quantity_used) VALUES (?, ?, ?)",
                (item_id, ingredient_ids[ingredient_name], quantity)
            )
        for subcategory_name, subcategory_price, subcategory_ingredients in SUBCATEGORIES:
            cursor.execute(
                "INSERT INTO Subcategories (item_id, name, price) VALUES (?, ?, ?)",
                (item_id, subcategory_name, subcategory_price)
            )
            subcategory_id = cursor.lastrowid
            for ingredient_name, quantity in subcategory_ingredients:
                cursor.execute(
                    "INSERT INTO Subcategories_Ingredients (subcategory_id, ingredient_id, quantity_used) VALUES (?, ?, ?)",
                    (subcategory_id, ingredient_ids[ingredient_name], quantity)
                )

    # links the Extra Boba options that were already in the database to the Boba ingredient
    cursor.execute("""
        INSERT OR IGNORE INTO Subcategories_Ingredients (subcategory_id, ingredient_id, quantity_used)
        SELECT subcategory_id, ?, 50 FROM Subcategories WHERE name = 'Extra Boba'
    """, (ingredient_ids["Boba"],))

    # Orders spread over the last 30 days, prices worked out from the items and options picked
    all_items = cursor.execute("SELECT item_id, price FROM Items").fetchall()
    for _ in range(NUMBER_OF_ORDERS):
        order_date = (date.today() - timedelta(days=random.randint(0, 29))).isoformat()
        cursor.execute("INSERT INTO Orders (date, price) VALUES (?, 0)", (order_date,))
        order_id = cursor.lastrowid
        total = 0
        for _ in range(random.randint(1, 4)): # 1 to 4 drinks per order
            item_id, item_price = random.choice(all_items)
            cursor.execute("INSERT INTO Ordered_Items (order_id, item_id) VALUES (?, ?)", (order_id, item_id))
            ordered_item_id = cursor.lastrowid
            total += item_price
            subcategories = cursor.execute(
                "SELECT subcategory_id, price FROM Subcategories WHERE item_id = ?", (item_id,)
            ).fetchall()
            for subcategory_id, subcategory_price in random.sample(subcategories, random.randint(0, min(2, len(subcategories)))):
                cursor.execute(
                    "INSERT INTO Ordered_Items_Subcategories (ordered_item_id, subcategory_id) VALUES (?, ?)",
                    (ordered_item_id, subcategory_id)
                )
                total += subcategory_price
        cursor.execute("UPDATE Orders SET price = ? WHERE order_id = ?", (total, order_id))

    conn.commit()
    conn.close()
    print("Sample data added.")


if __name__ == "__main__":
    db.create_tables()
    seed()
